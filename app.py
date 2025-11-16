from flask import Flask, request, jsonify
import threading
import time
import os
import requests
from requests_oauthlib import OAuth1

app = Flask(__name__)

def delete_after_delay(auth, post_id):
    time.sleep(600)  # 10分後に削除
    url = f"https://api.x.com/2/tweets/{post_id}"
    res = requests.delete(url, auth=auth)
    print("削除:", res.text)

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    print("受信:", data)

    text = data.get("text")
    consumer_key = data.get("consumer_key")
    consumer_secret = data.get("consumer_secret")
    access_token = data.get("access_token")
    access_token_secret = data.get("access_token_secret")

    auth = OAuth1(
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret
    )

    # 投稿
    url = "https://api.x.com/2/tweets"
    payload = {"text": text}
    res = requests.post(url, json=payload, auth=auth)
    print("投稿:", res.text)

    # 投稿ID → 削除予約
    try:
        post_id = res.json()["data"]["id"]
        threading.Thread(target=delete_after_delay, args=(auth, post_id), daemon=True).start()
    except Exception as e:
        print("投稿ID取得失敗:", e)

    return jsonify({"status": "ok"})
