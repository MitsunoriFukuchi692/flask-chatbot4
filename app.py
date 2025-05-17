import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
import openai

# Flask App Initialization
app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

# Rate Limiter
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

# Load API keys from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Ensure Google credentials
if not google_credentials or not os.path.exists(google_credentials):
    raise Exception("Google Cloud credentials file not found.")

# Routes
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
            return jsonify({"reply": "申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"}), 200

        messages = [
            {"role": "system", "content": "あなたは老人を元気づける日本語を話す心優しいアシスタントです。"},
            {"role": "user", "content": user_text}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )

        reply = response.choices[0].message.content.strip()[:200]

        # Google TTS
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        tts_response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        if not os.path.exists("static"):
            os.makedirs("static")

        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        # Save chat log
        with open("chatlog.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"ユーザー: {user_text}\nみまくん: {reply}\n---\n")

        return jsonify({"reply": reply})

    except Exception as e:
        print("⚠️ エラー:", str(e))
        return jsonify({"reply": "エラーが発生しました。"}), 500

@app.route("/logs")
def logs():
    try:
        with open("chatlog.txt", "r", encoding="utf-8") as log_file:
            logs = log_file.read()
        return f"<pre>{logs}</pre><br><a href='/download-log'>ログをダウンロード</a>"
    except FileNotFoundError:
        return "ログファイルが見つかりません。"

@app.route("/download-log")
def download_log():
    return app.send_static_file("chatlog.txt")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)