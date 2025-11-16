import time
import logging
from flask import Flask, request, jsonify
from requests_oauthlib import OAuth1Session

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


@app.route("/", methods=["POST"])
def receive():
    try:
        data = request.json
        accounts = data.get("accounts", [])

        logging.info("==> 受信: %s", data)

        for i, acc in enumerate(accounts):
            text = acc.get("text", "")

            delay_min = i * 10
            logging.info("[INFO] %d番目アカウント → %d 分遅延して投稿開始", i, delay_min)

            time.sleep(delay_min * 60)

            tweet_id = post_tweet(acc, text)
            logging.info("[INFO] 投稿ID: %s", tweet_id)

        return jsonify({"status": "ok"})

    except Exception as e:
        logging.error("[ERROR] 受信エラー: %s", str(e))
        return jsonify({"error": str(e)}), 500


def post_tweet(account, text):
    try:
        oauth = OAuth1Session(
            client_key=account["consumer_key"],
            client_secret=account["consumer_secret"],
            resource_owner_key=account["access_token"],
            resource_owner_secret=account["access_token_secret"]
        )

        url = "https://api.twitter.com/1.1/statuses/update.json"

        params = {"status": text}
        response = oauth.post(url, params=params)

        if response.status_code != 200:
            logging.error("[ERROR] 投稿失敗: %s", response.text)
            raise Exception("Twitter API Error")

        result = response.json()
        return result["id_str"]

    except Exception as e:
        logging.error("[ERROR] 投稿処理で例外: %s", str(e))
        raise e


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
