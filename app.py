
import os
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import openai
from gtts import gTTS

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

openai.api_key = os.getenv("OPENAI_API_KEY")
LOG_FILE = "chatlog.txt"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/speak")
def speak():
    return render_template("speak.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    user_text = request.json.get("user_text", "").strip()
    if not user_text:
        return jsonify({"error": "メッセージが空です"}), 400

    if len(user_text) > 100:
        return jsonify({"reply": "申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"}), 200

    try:
        messages = [{"role": "user", "content": user_text}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        reply = response.choices[0].message["content"].strip()
        if len(reply) > 200:
            reply = reply[:200] + "…"

        # 音声生成
        tts = gTTS(reply, lang="ja")
        tts.save("static/output.mp3")

        # ログ保存
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"ユーザー: {user_text}\n")
            log.write(f"ボット: {reply}\n")

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logs", methods=["GET"])
def get_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.read()
        return f"<pre>{logs}</pre>"
    except FileNotFoundError:
        return "ログファイルが見つかりません。"

@app.route("/download_logs", methods=["GET"])
def download_logs():
    return send_file(LOG_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
