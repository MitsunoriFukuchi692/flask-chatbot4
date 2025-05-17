
import os
import json
import time
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
from openai import OpenAI

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

openai_api_key = os.getenv("OPENAI_API_KEY")
google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
assert openai_api_key, "OpenAI API key not found."
assert google_application_credentials, "Google Cloud credentials not found."

client = OpenAI(api_key=openai_api_key)
tts_client = texttospeech.TextToSpeechClient()

@app.route("/")
def index():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    try:
        data = request.get_json()
        user_text = data.get("text", "").strip()

        if len(user_text) > 100:
            reply_text = "申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"
        else:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "あなたは心優しい高齢者見守りロボット「みまくん」です。語尾は丁寧で、短めに答えます。"},
                    {"role": "user", "content": user_text}
                ]
            )
            reply_text = response.choices[0].message.content.strip()[:200]

            synthesis_input = texttospeech.SynthesisInput(text=reply_text)
            voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            os.makedirs("static", exist_ok=True)
            with open("static/output.mp3", "wb") as out:
                out.write(tts_response.audio_content)

        with open("chatlog.txt", "a", encoding="utf-8") as log:
            log.write(f"🧑 {user_text}\n🤖 {reply_text}\n---\n")

        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"reply": "エラーが発生しました。"}), 500

@app.route("/logs")
def logs():
    return send_file("chatlog.txt", mimetype="text/plain")

@app.route("/download-log")
def download_log():
    return send_file("chatlog.txt", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
