from flask import Flask, request, jsonify
import threading
import time
import requests
import os

app = Flask(__name__)

def delete_after_delay(bearer, post_id, delay):
    time.sleep(delay)  # 遅延して削除
    url = f"https://api.x.com/2/tweets/{post_id}"
    headers = {"Authorization": f"Bearer {bearer}"}
    res = requests.delete(url, headers=headers)
    print(f"[削除] {post_id} → {res.text}")

def post_with_delay(index, consumer_key, consumer_secret, access_token, access_token_secret, text):
    # アカウントごとに10分ずつズラす
    delay = index * 600  
    print(f"[INFO] {index}番目アカウント → {delay/60} 分遅延して投稿開始")

    time.sleep(delay)

    url = "https://api.x.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}

    res = requests.post(url, json=payload, headers=headers)
    print("[投稿]:", res.text)

    try:
        post_id = res.json()["data"]["id"]
        print(f"[投稿成功] post_id={post_id}")

        # さらに10分後に削除
        threading.Thread(
            target=delete_after_delay,
            args=(access_token, post_id, 600),
            daemon=True
        ).start()
    except:
        print("[ERROR] 投稿ID取得失敗")


@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    print("[受信]", data)

    accounts = data.get("accounts", [])

    for index, acc in enumerate(accounts):
        threading.Thread(
            target=post_with_delay,
            args=(
                index,
                acc["consumer_key"],
                acc["consumer_secret"],
                acc["access_token"],
                acc["access_token_secret"],
                acc["text"]
            ),
            daemon=True
        ).start()

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
