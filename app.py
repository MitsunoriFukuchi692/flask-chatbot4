
import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from google.cloud import texttospeech
import openai

# 環境変数の読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

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
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        if len(user_text) > 100:
            return jsonify({"reply": "みまくん: 申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"})

        messages = [
            {"role": "system", "content": "あなたは高齢者の話し相手になる、やさしい日本語で答えるアシスタントです。"},
            {"role": "user", "content": user_text}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )

        reply_text = response.choices[0].message.content.strip()
        if len(reply_text) > 200:
            reply_text = reply_text[:200] + "..."

        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        tts_response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        if not os.path.exists("static"):
            os.makedirs("static")

        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        # 会話ログの保存
        with open("chatlog.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"👤 User: {user_text}\n🤖 Mima-kun: {reply_text}\n---\n")

        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"reply": f"エラーが発生しました: {str(e)}"}), 500

@app.route("/logs")
def get_logs():
    return send_from_directory(directory=".", path="chatlog.txt", as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
