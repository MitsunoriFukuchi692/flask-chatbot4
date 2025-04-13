
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

# OpenAI APIキー（環境変数から取得）
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    user_message = data.get("message") if data else ""

    if not user_message:
        return jsonify({"reply": "⚠️ メッセージが空です。"})

    try:
        # OpenAI v1.0+ 形式の API 呼び出し
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """あなたはロボ・スタディ株式会社の公式チャットボットです。以下の情報を参考に、正確に応答してください：

"""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ エラーが発生しました: {str(e)}"})

if __name__ == "__main__":
    app.run()
