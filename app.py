from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

openai.api_key = os.environ.get("OPENAI_API_KEY")

system_message = """AI・みまくんは、人々の孤独を防ぐために作られた、小型で可愛い、見守り対話ロボットです。
高齢者を中心の支えとなることを目的に開発され、ChatGPTと連携して自由な会話が可能です。
価格は198,000円（税込）で、Wi-Fiに接続して自動アップデートされます。
"""

def save_chat_to_json(user_message, bot_response):
    log_entry = {
        "created_at": datetime.now().isoformat(),
        "user": user_message,
        "bot": bot_response
    }
    with open("chat_logs.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    if not user_message:
        return jsonify({"error": "メッセージがありません"}), 400

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        bot_reply = response.choices[0].message["content"].strip()

        # ✅ ログをJSONに保存
        save_chat_to_json(user_message, bot_reply)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "AI・みまくん Flask サーバーが起動中です"

if __name__ == "__main__":
    app.run(debug=True)
