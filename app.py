
import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
from openai import OpenAI
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

openai_api_key = os.getenv("OPENAI_API_KEY")
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
assert openai_api_key, "OpenAI API key not set"
assert google_credentials, "Google credentials not set"
client = OpenAI(api_key=openai_api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/logs")
def logs():
    return render_template("logs.html")

@app.route("/chatlog.txt")
def download_log():
    return send_file("chatlog.txt", as_attachment=True)

@app.route("/chat", methods=["POST"])
@limiter.limit("1 per second")
def chat():
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        if len(user_text) > 100:
            return jsonify({"reply": "申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは高齢者を優しく励ます日本語のアシスタントです。返答は200文字以内にしてください。"},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message.content.strip()[:200]

        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        os.makedirs("static", exist_ok=True)
        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("chatlog.txt", "a", encoding="utf-8") as log:
            log.write(f"{timestamp}\nあなた: {user_text}\nみまくん: {reply_text}\n\n")

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("⚠️ エラー:", str(e), flush=True)
        return jsonify({"reply": "みまくん: エラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
