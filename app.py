from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins="https://robostudy.jp")  # 必要に応じて ["https://robostudy.jp"] に変更可能

# セキュアな環境変数からAPIキーを取得
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}]
    )
    return jsonify({"reply": response.choices[0].message['content']})

if __name__ == "__main__":
    app.run()
