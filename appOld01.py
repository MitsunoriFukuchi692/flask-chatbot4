import os
import time
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from openai import OpenAI
from google.cloud import texttospeech
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])  # ← CORS設定

limiter = Limiter(key_func=get_remote_address, default_limits=["5 per minute"])
limiter.init_app(app)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
client = OpenAI(api_key=openai_api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("1 per second")  # 秒間連打制限
def chat():
    try:
        data = request.get_json()
        user_text = data.get("text", "").strip()
        if len(user_text) > 100:
            return jsonify({"reply": "申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"})

        messages = [
            {"role": "system", "content": "あなたは高齢者を励ます優しい日本語アシスタントです。語尾は柔らかく。"},
            {"role": "user", "content": user_text}
        ]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        reply = response.choices[0].message.content.strip()[:200]

        log_entry = f"👤 {user_text}\n🤖 {reply}\n---\n"
        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)

        # 音声合成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response_tts = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        output_path = Path("static/output.mp3")
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "wb") as out:
            out.write(response_tts.audio_content)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "エラーが発生しました。"}), 500

@app.route("/logs")
def logs():
    return send_file("chatlog.txt", as_attachment=False)

@app.route("/download")
def download():
    return send_file("chatlog.txt", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
