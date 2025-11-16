import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# =============================
# Googleスプレッドシート設定
# =============================
SPREADSHEET_KEY = "1jd3sxVzZXKtWIU5fVNARHb69B2SIZ3B5FyzcjaXv2pY"
SHEET_NAME = "Accounts"  # ← シートタブ名に合わせて変更（例: Sheet1なら "Sheet1"）

scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"
         ]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)

# =============================
# Chrome設定
# =============================
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--start-maximized")

print("🚀 自動投稿＆削除スクリプト（Selenium版）開始")

rows = sheet.get_all_records()
print(f"▶ {len(rows)} 行を読み込みました\n")

# =============================
# アカウントループ
# =============================
for row in rows:
    account = row.get("AccountName")
    password = row.get("Password")
    active = str(row.get("Active")).lower()
    post_text = row.get("PostText")
    post_time_str = str(row.get("PostTime"))
    delete_after = row.get("DeleteAfter(min)")

    # データが欠落している行をスキップ
    if not account or not password or not post_text or not post_time_str:
        print(f"⚠️ [{account or '不明なアカウント'}] の行に欠落があります。スキップします。")
        continue

    # Activeフラグ確認
    if active not in ["1", "true", "yes", "on"]:
        print(f"⏩ {account} は非アクティブ。スキップします。")
        continue

    # 時刻のパース
    try:
        # 「2025-11-13 05:30」形式 または 「05:30」形式対応
        if len(post_time_str) <= 5:
            now = datetime.now()
            post_time = datetime.strptime(f"{now.strftime('%Y-%m-%d')} {post_time_str}", "%Y-%m-%d %H:%M")
        else:
            post_time = datetime.strptime(post_time_str, "%Y-%m-%d %H:%M")
    except Exception:
        print(f"⚠️ {account} の投稿時間エラー: {post_time_str}")
        continue

    # 投稿時刻まで待機
    now = datetime.now()
    wait_seconds = (post_time - now).total_seconds()
    if wait_seconds > 0:
        print(f"\n⏳ {account} の投稿予定: {post_time.strftime('%Y-%m-%d %H:%M:%S')} JST")
        print(f"🕓 {int(wait_seconds)} 秒待機します...")
        time.sleep(wait_seconds)

    # =============================
    # Seleniumで投稿
    # =============================
    try:
        print(f"🚀 {account} にログイン中...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://twitter.com/login")
        time.sleep(5)

        # ログイン画面：ユーザー名入力
        user_input = driver.find_element(By.NAME, "text")
        user_input.send_keys(account)
        user_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # パスワード入力
        pwd_input = driver.find_element(By.NAME, "password")
        pwd_input.send_keys(password)
        pwd_input.send_keys(Keys.RETURN)
        time.sleep(5)

        # 投稿フィールドに移動して投稿
        print(f"✏️ {account} でツイート投稿中...")
        tweet_box = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Tweet text']")
        tweet_box.send_keys(post_text)
        time.sleep(1)
        tweet_box.send_keys(Keys.COMMAND, Keys.RETURN)  # macOS用ショートカット
        print(f"✅ {account} の投稿が完了しました。")

        # 削除スケジュール
        if delete_after:
            delete_after = int(delete_after)
            delete_time = datetime.now() + timedelta(minutes=delete_after)
            print(f"🗑 {delete_after} 分後（{delete_time.strftime('%H:%M')}）に削除予定です。")

        driver.quit()

    except NoSuchElementException as e:
        print(f"⚠️ {account} のログインまたは投稿でエラー発生: {e}")
        driver.quit()
        continue

print("\n🎉 全ての投稿処理が完了しました！")
