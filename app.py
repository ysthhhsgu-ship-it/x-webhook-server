from flask import Flask, request, jsonify
import threading
import time
import requests
import os

app = Flask(__name__)

def delete_after_delay(bearer, post_id):
    time.sleep(600)  # 10分
    url = f"https://api.x.com/2/tweets/{post_id}"
    headers = {"Authorization": f"Bearer {bearer}"}
    res = requests.delete(url, headers=headers)
    print("削除:", res.text)

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    print("受信:", data)

    text = data.get("text")
    bearer = data.get("bearer")

    # X投稿
    url = "https://api.x.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}

    res = requests.post(url, json=payload, headers=headers)
    print("投稿:", res.text)

    # 投稿成功 → 削除予約
    try:
        post_id = res.json()["data"]["id"]
        threading.Thread(target=delete_after_delay, args=(bearer, post_id), daemon=True).start()
    except Exception as e:
        print("投稿ID取得失敗:", e)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway用
    app.run(host="0.0.0.0", port=port)
