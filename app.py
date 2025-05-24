
import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from google.cloud import texttospeech
from openai import OpenAI
from pathlib import Path
import dotenv

# .envファイルの読み込み
config = dotenv.dotenv_values(Path('.env'))

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

openai_api_key = os.getenv("OPENAI_API_KEY")
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
assert openai_api_key, "OpenAI API key is missing."
assert google_credentials, "Google Cloud credentials are missing."

openai_client = OpenAI(api_key=config["OPENAI_API_KEY"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/speak")
def speak():
    return render_template("speak.html")

@app.route("/logs")
def logs():
    if os.path.exists("chatlog.txt"):
        return send_file("chatlog.txt", mimetype="text/plain", as_attachment=True)
    return "ログファイルが存在しません。", 404

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        if len(user_text) > 100:
            return jsonify({"reply": "みまくん: 申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"})

        messages = [
            {"role": "system", "content": "あなたは高齢者に寄り添い、親しみやすく丁寧に日本語で応答するロボットです。語尾には少しだけ関西弁が混じることもあります。"},
            {"role": "user", "content": user_text}
        ]
        chat_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        reply = chat_response.choices[0].message.content.strip()
        if len(reply) > 200:
            reply = reply[:200] + "..."

        # 音声合成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        
        os.makedirs("static", exist_ok=True)
        with open("static/output.mp3", "wb") as out:
            out.write(tts_response.audio_content)

        # 会話ログ保存
        with open("chatlog.txt", "a", encoding="utf-8") as log:
            log.write(f"🧑 ユーザー: {user_text}\n")

🤖 Bot: {reply}

")

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ エラーが発生しました: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
