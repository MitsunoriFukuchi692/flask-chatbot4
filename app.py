import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import openai

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["5 per minute"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    data = request.get_json()
    user_text = data.get("text", "")[:100]  # 入力文字数制限

    if not user_text:
        return jsonify({"reply": "メッセージが空です。"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}],
            api_key=openai_api_key
        )
        reply = response.choices[0].message["content"].strip()[:200]  # 応答文字数制限
    except Exception as e:
        reply = "エラーが発生しました。"

    with open("chatlog.txt", "a", encoding="utf-8") as log:
        log.write(f"ユーザー: {user_text}\n")
        log.write(f"みまくん: {reply}\n\n")

    return jsonify({"reply": reply})

@app.route("/logs")
def logs():
    try:
        with open("chatlog.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except FileNotFoundError:
        return "ログがまだ存在しません。"

if __name__ == "__main__":
    app.run(debug=True)