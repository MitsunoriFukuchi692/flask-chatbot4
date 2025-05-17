import os
import json
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
from openai import OpenAI
from pathlib import Path
import dotenv

# Flask アプリの初期化
app = Flask(__name__)

# レート制限の設定（1分間に10回まで）
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

# 環境変数の読み込み
secret_fullpath = Path('.env')
config = dotenv.dotenv_values(secret_fullpath)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

assert openai_api_key, "OpenAI API key is not set."
assert google_application_credentials, "Google Cloud credentials are not set."

openai_client = OpenAI(api_key=config["OPENAI_API_KEY"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("10 per minute")  # レート制限：1分間に10回まで
def chat():
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        print("✅ USER TEXT:", user_text, flush=True)

        if len(user_text) > 100:
            return jsonify({"reply": "みまくん: 申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"})

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは老人を元気づける日本語を話す心優しいアシスタントです。"},
                {"role": "user", "content": user_text}
            ]
        )

        reply_text = response.choices[0].message.content.strip()[:200]  # 応答も200文字以内
        print("🤖 ChatGPT 応答:", reply_text, flush=True)

        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        if not os.path.exists("static"):
            os.makedirs("static")

        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("⚠️ 全体の処理エラー:", str(e), flush=True)
        return jsonify({"reply": "エラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
