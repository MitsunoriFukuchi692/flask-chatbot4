
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

openai.api_key = os.environ.get("OPENAI_API_KEY")

SUPABASE_URL = "https://uvseetukwotbmyqdfcaj.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2VldHVrd290Ym15cWRmY2FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTMwNzEzNDcsImV4cCI6MjAyODY0NzM0N30.9ALYMEaJWn51LuJ1byB3A8ADrTXMNBbHUqJXZ8o8xnQ"
TABLE_NAME = "chat_logs"

def save_to_supabase(user_message, bot_reply):
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    data = {
        "user": user_message,
        "bot": bot_reply
    }
    r = requests.post(url, json=data, headers=headers)
    print("Supabase保存:", r.status_code, r.text)

system_message = """AI・みまくんは、人々の孤独を防ぐために作られた、小型で可愛い、見守り対話ロボットです。
高齢者の心の支えとなることを目的に開発され、ChatGPTと連携して自由な会話が可能です。
価格は198,000円（税込）で、Wi-Fiに接続して自動アップデートされます。

ロボ・スタディ株式会社へのお問い合わせは、以下の方法をご利用ください：
・メール：info@robostudy.jp
・電話：090-3919-7376
・公式サイト：https://robostudy.jp
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "⚠️ メッセージが空です。"})

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content

        save_to_supabase(user_message, reply)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ エラーが発生しました: {str(e)}"})

if __name__ == "__main__":
    app.run()
