import time
import gspread
from google.oauth2.service_account import Credentials
import tweepy
from datetime import datetime, timedelta, timezone

# ======== 設定（ここをあなたの環境に合わせて変更） ========
SPREADSHEET_NAME = "埼玉地方"   # ← スプレッドシート名（ファイル名）
WORKSHEET_NAME = "Accounts"     # ← タブ名（完全一致）
POST_INTERVAL = 10             # 投稿間隔（秒）= 10分（各投稿後に待つ）
JST = timezone(timedelta(hours=9))  # 日本時間
START_HOUR = 0                  # 稼働開始 7:00
END_HOUR = 24                   # 稼働終了 24:00
# ============================================================

# Google Sheets 認証（credentials.json を同フォルダに置くこと）
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
worksheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

# 期待するヘッダー順（シートに合わせて編集可能）
expected_headers = [
    "NO", "AccountName", "API_KEY", "API_SECRET",
    "ACCESS_TOKEN", "ACCESS_SECRET", "Active", "PostText", "PostTime", "DeleteAfter(min)"
]
records = worksheet.get_all_records(expected_headers=expected_headers)

print("🚀 自動投稿＆削除スクリプト（スケジュール版）開始")
print(f"▶ {len(records)} 行を読み込みました\n")

for idx, row in enumerate(records, start=1):
    # Active チェック
    if str(row.get("Active", "")).strip().lower() not in ("true", "yes", "1", "on"):
        continue

    account = row.get("AccountName", "<unknown>")
    post_text = str(row.get("PostText", "")).strip()
    post_time_str = str(row.get("PostTime", "")).strip()
    try:
        delete_after_min = int(row.get("DeleteAfter(min)", 30))
    except:
        delete_after_min = 30
    delete_after = delete_after_min * 60  # 秒

    if not post_text or not post_time_str:
        print(f"⚠️ {account} の PostText または PostTime が未設定。スキップします。")
        continue

    # PostTime 解析（HH:MM）
    try:
        post_hour, post_min = map(int, post_time_str.split(":"))
    except Exception as e:
        print(f"⚠️ {account} の PostTime 形式が不正（例: 07:30）。スキップ: {e}")
        continue

    # 現在時刻（JST）
    now = datetime.now(JST)
    # 稼働時間チェック
    if not (START_HOUR <= now.hour < END_HOUR):
        print(f"🕒 現在時刻 {now.strftime('%H:%M')} は稼働時間外（{START_HOUR}:00〜{END_HOUR}:00）。スキップ。")
        continue

    # 投稿予定時刻（今日の指定時刻）を計算
    target_time = now.replace(hour=post_hour, minute=post_min, second=0, microsecond=0)
    if target_time < now:
        # すでに過ぎていれば翌日に回す
        target_time += timedelta(days=1)

    wait_sec = (target_time - now).total_seconds()
    print(f"⏳ {account} の投稿予定: {target_time.strftime('%Y-%m-%d %H:%M:%S')}（あと {wait_sec/60:.1f} 分）")

    # 待機してから投稿
    if wait_sec > 0:
        time.sleep(wait_sec)

    # 投稿処理
    try:
        auth = tweepy.OAuth1UserHandler(
            row["API_KEY"],
            row["API_SECRET"],
            row["ACCESS_TOKEN"],
            row["ACCESS_SECRET"]
        )
        api = tweepy.API(auth)

        tweet = api.update_status(post_text)
        print(f"✅ {account} 投稿完了: https://x.com/{account}/status/{tweet.id}")

        # 削除待ち
        print(f"🕒 {delete_after_min} 分後に削除予定...")
        time.sleep(delete_after)

        # 削除実行
        api.destroy_status(tweet.id)
        print(f"🗑️ {account} 投稿削除完了\n")

    except Exception as e:
        print(f"❌ {account} の投稿/削除でエラー発生: {e}\n")

    # 投稿間のインターバル（次のアカウントまで）
    print(f"⏸️ 次の投稿まで {POST_INTERVAL/60:.1f} 分待機します...\n")
    time.sleep(POST_INTERVAL)

print("✨ 全件処理が完了しました。")

