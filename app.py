
import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
from openai import OpenAI
import dotenv
from pathlib import Path
import time

# .envファイルから環境変数読み込み
dotenv.load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["5 per minute"])

openai_api_key = os.getenv("OPENAI_API_KEY")
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

assert openai_api_key, "OpenAI API key is not set."
assert google_credentials, "Google Cloud credentials are not set."

openai_client = OpenAI(api_key=openai_api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    try:
        data = request.get_json()
        user_text = data.get("text", "").strip()

        if len(user_text) > 100:
            return jsonify({"reply": "申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"})

        messages = [
            {"role": "system", "content": "あなたは高齢者をやさしく励ますロボット、みまくんです。"},
            {"role": "user", "content": user_text}
        ]

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )

        reply_text = response.choices[0].message.content.strip()

        # Google TTS
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        if not os.path.exists("static"):
            os.makedirs("static")

        with open("static/output.mp3", "wb") as out:
            out.write(tts_response.audio_content)

        # 会話ログ保存
        with open("chatlog.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"🧑 {user_text}\n🤖 {reply_text}\n\n")

        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"reply": "エラーが発生しました。"}), 500

@app.route("/logs")
def show_logs():
    log_path = "chatlog.txt"
    if not os.path.exists(log_path):
        return "ログがまだありません。"
    return send_file(log_path, as_attachment=False, mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
