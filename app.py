
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])  # 本番ドメイン限定

# OpenAI APIキー（環境変数）
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    user_message = data.get("message") if data else ""

    if not user_message:
        return jsonify({"reply": "⚠️ メッセージが空です。"})

    try:
        # 新しいAPI書き方（openai>=1.0.0）
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ エラーが発生しました: {str(e)}"})

if __name__ == "__main__":
    app.run()
