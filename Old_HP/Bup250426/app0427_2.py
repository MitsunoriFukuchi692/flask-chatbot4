from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

# OpenAI APIキーを環境変数から取得
openai.api_key = os.environ.get("OPENAI_API_KEY")

# システムプロンプト
system_message = """AI・みまくんは、人々の孤独を防ぐために作られた、小型で可愛い、見守り対話ロボットです。
高齢者の心の支えとなることを目的に開発され、ChatGPTと連携して自由な会話が可能です。
価格は198,000円（税込）で、Wi-Fiに接続して自動アップデートされます。"""

# JSONにチャットログを保存
def save_chat_to_json(user_message, bot_response):
    log = {
        "created_at": datetime.now().isoformat(),
        "user": user_message,
        "bot": bot_response
    }
    with open("chat_logs.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

# チャットAPIエンドポイント
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("user_message", "").strip()

    if not user_message:
        return jsonify({"reply": "⚠️ メッセージが空です"}), 400

    try:
        # OpenAIのAPIでメッセージを処理
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        bot_reply = response.choices[0].message["content"].strip()

        # チャットログをJSONに保存
        save_chat_to_json(user_message, bot_reply)

        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ エラーが発生しました: {str(e)}"}), 500

@app.route("/")
def index():
    return "AI・みまくん Flask サーバー起動中"

if __name__ == "__main__":
    app.run(debug=True)
