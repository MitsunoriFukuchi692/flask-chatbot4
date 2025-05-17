
import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from google.cloud import texttospeech
from openai import OpenAI
from pathlib import Path
import dotenv

# 環境変数の読み込み
config = dotenv.dotenv_values(Path(".env"))
openai_api_key = config.get("OPENAI_API_KEY")
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app = Flask(__name__)
client = OpenAI(api_key=openai_api_key)
log_file = "chatlog.txt"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        if not user_text:
            return jsonify({"reply": "入力が空です。"}), 400

        if len(user_text) > 100:
            return jsonify({"reply": "入力は100文字以内でお願いします。"}), 400

        print("📥 User:", user_text, flush=True)

        # ChatGPT応答生成
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは親切で丁寧な会社案内チャットボットです。"},
                {"role": "user", "content": user_text}
            ]
        )
        reply = response.choices[0].message.content.strip()
        reply = reply[:200]
        print("🤖 Reply:", reply, flush=True)

        # ログ保存
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"User: {user_text}\nBot: {reply}\n\n")

        # 音声合成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        if not os.path.exists("static"):
            os.makedirs("static")
        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        return jsonify({"reply": reply})

    except Exception as e:
        print("⚠️ Error:", str(e), flush=True)
        return jsonify({"reply": "エラーが発生しました。"}), 500

@app.route("/logs")
def logs():
    return send_file(log_file, mimetype="text/plain", as_attachment=False)
