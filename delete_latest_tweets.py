import gspread
from google.oauth2.service_account import Credentials
import tweepy

# ======== 設定 ========
SPREADSHEET_NAME = "埼玉地方"   # ← あなたのスプレッドシート名に変更
WORKSHEET_NAME = "Accounts"     # ← シート名（タブ名が完全一致しているか確認）
# ======================

# Google Sheets 認証（credentials.json を同フォルダに配置）
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

# スプレッドシートとシートを開く
spreadsheet = client.open(SPREADSHEET_NAME)
worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

# ✅ ヘッダーを明示的に指定して、空白や重複セルを無視
expected_headers = ["NO", "AccountName", "API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_SECRET", "Active"]
records = worksheet.get_all_records(expected_headers=expected_headers)

# ===================== メイン処理 =====================
for row in records:
    # Active 列が True／Yes／1／On のものだけ実行
    if str(row.get("Active", "")).strip().lower() in ("true", "yes", "1", "on"):
        account = row.get("AccountName", "<unknown>")
        print(f"▶ {account} の最新ポストを削除中...")

        try:
            # Tweepy 認証設定
            auth = tweepy.OAuth1UserHandler(
                row["API_KEY"],
                row["API_SECRET"],
                row["ACCESS_TOKEN"],
                row["ACCESS_SECRET"]
            )
            api = tweepy.API(auth)

            # 最新ツイートを取得
            tweets = api.user_timeline(count=1, tweet_mode="extended")
            if not tweets:
                print(f"⚠️ {account} に削除対象のツイートがありません。")
                continue

            latest_tweet = tweets[0]
            tweet_id = latest_tweet.id

            # 削除対象ツイートを表示
            preview = (
                latest_tweet.full_text[:80] + "..."
                if len(latest_tweet.full_text) > 80
                else latest_tweet.full_text
            )
            print(f"🗑️ 削除対象: {preview}")

            # 削除実行
            api.destroy_status(tweet_id)
            print(f"✅ {account}: ツイート削除完了\n")

        except Exception as e:
            print(f"❌ {account} の処理中にエラー発生: {e}\n")
