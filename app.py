import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from google.cloud import texttospeech
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# .env 読み込み（ローカル用）
if Path(".env").exists():
    load_dotenv()

# 環境変数からAPIキー取得
openai_api_key = os.getenv("OPENAI_API_KEY")
google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

assert openai_api_key, "❌ OPENAI_API_KEY is not set"
assert google_credentials_path, "❌ GOOGLE_APPLICATION_CREDENTIALS is not set"

# OpenAIクライアント初期化
openai_client = OpenAI(api_key=openai_api_key)

# Flask アプリ作成
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
@cross_origin(origins=["https://robostudy.jp", "http://localhost:10000"])
def chat():
    try:
        print("📥 RAW REQUEST:", request.data, flush=True)
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        print("✅ USER TEXT:", user_text, flush=True)
        print("🔑 OPENAI_API_KEY:", openai_api_key, flush=True)
        print("🔑 GOOGLE_APPLICATION_CREDENTIALS:", google_credentials_path, flush=True)

        # ChatGPT 応答取得
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは老人を元気づける日本語を話す心優しいアシスタントです。"},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message.content.strip()
        print("🤖 ChatGPT 応答:", reply_text, flush=True)

        # 音声合成
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

        print("✅ 音声ファイル保存:", output_path, flush=True)
        print("📦 サイズ:", os.path.getsize(output_path), "bytes", flush=True)

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("⚠️ エラー:", str(e), flush=True)
        return jsonify({"reply": "サーバーでエラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
