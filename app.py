from flask import Flask, request, jsonify
import tweepy
import os
import traceback

app = Flask(__name__)

@app.route("/", methods=["POST"])
def receive():
    try:
        data = request.json
        accounts = data.get("accounts", [])

        results = []

        for acc in accounts:
            consumer_key = acc["consumer_key"]
            consumer_secret = acc["consumer_secret"]
            access_token = acc["access_token"]
            access_token_secret = acc["access_token_secret"]
            text = acc["text"]

            auth = tweepy.OAuth1UserHandler(
                consumer_key, consumer_secret,
                access_token, access_token_secret
            )
            api = tweepy.API(auth)

            try:
                tweet = api.update_status(text)
                results.append({"id": tweet.id})
            except Exception as e:
                print("Twitter API ERROR:", e)
                print(traceback.format_exc())
                results.append({"error": str(e)})
                # 投稿失敗しても続ける

        return jsonify({"status": "ok", "results": results})

    except Exception as e:
        print("SYSTEM ERROR:", e)
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def health_check():
    return "OK - Python Flask server running", 200
