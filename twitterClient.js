import { TwitterApi } from "twitter-api-v2";

export async function postTweet(account, text) {
  try {
    const client = new TwitterApi({
      appKey: account.consumer_key,
      appSecret: account.consumer_secret,
      accessToken: account.access_token,
      accessSecret: account.access_token_secret
    });

    const v1 = client.v1;

    const result = await v1.tweet(text);

    return result.id_str;
  } catch (err) {
    console.error("[ERROR] 投稿失敗:", err);
    throw err;
  }
}
