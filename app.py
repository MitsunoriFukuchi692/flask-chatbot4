from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import openai
import traceback

# .envからAPIキーを読み込む
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# CORSの設定（robostudy.jpからのアクセスを許可）
CORS(app, resources={r"/chat": {"origins": "https://robostudy.jp"}})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切なアシスタントです。"},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        traceback.print_exc()  # ターミナルにエラーを出力
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
