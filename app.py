import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from google.cloud import texttospeech
from openai import OpenAI
from pathlib import Path
import dotenv

# .env の読み込み
dotenv.load_dotenv()

# Flask アプリと CORS の設定
app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

# 環境変数の確認
openai_api_key = os.getenv("OPENAI_API_KEY")
google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

assert openai_api_key, "OpenAI API key is not set in environment variables."
assert google_application_credentials, "Google Cloud credentials are not set in environment variables."

print("\U0001F511 OPENAI_API_KEY:", openai_api_key, flush=True)
print("\U0001F511 GOOGLE_APPLICATION_CREDENTIALS:", google_application_credentials, flush=True)

# OpenAI クライアントの初期化
openai_client = OpenAI(api_key=openai_api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        print("\U0001F4E5 RAW REQUEST:", request.data, flush=True)
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        print("\u2705 USER TEXT:", user_text, flush=True)

        # OpenAI Chat API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは老人を元気づける日本語を話す心優しいアシスタントです。会社名はロボ・スタディ株式会社、製品名はAIみまくんです。会社や製品に関する質問には簡潔に正確に答えてください。"},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message.content.strip()
        print("\U0001F916 ChatGPT 応答:", reply_text, flush=True)

        # Google Cloud TTS
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        # static/output.mp3 に保存
        if not os.path.exists("static"):
            os.makedirs("static")
            print("\u2705 staticフォルダを作成しました。", flush=True)
        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        print("\u2705 音声ファイルサイズ:", os.path.getsize(output_path), "bytes", flush=True)
        return jsonify({"reply": reply_text})

    except Exception as e:
        print("\u26A0\uFE0F 全体の処理エラー:", str(e), flush=True)
        return jsonify({"reply": "エラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
