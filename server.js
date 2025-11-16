import express from "express";
import { postTweet } from "./twitterClient.js";

const app = express();
app.use(express.json());

// Google Apps Script → Render
app.post("/", async (req, res) => {
  try {
    console.log("==> 受信", req.body);
    const { accounts, text } = req.body;

    for (let i = 0; i < accounts.length; i++) {
      const acc = accounts[i];

      console.log(`[INFO] ${i}番目アカウント → 投稿開始`);

      const id = await postTweet(acc, text);

      console.log("[INFO] 投稿ID:", id);
    }

    res.json({ status: "ok" });
  } catch (err) {
    console.error("[ERROR] 受信エラー", err);
    res.status(500).json({ error: err.toString() });
  }
});

// Render は PORT を環境変数から取得する必要あり
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
