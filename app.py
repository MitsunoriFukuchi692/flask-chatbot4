

import os
import json
from flask import Flask, render_template, request, jsonify
from google.cloud import texttospeech
import openai
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

app = Flask(__name__)

# OpenAI APIキーとGoogle Cloud認証情報の読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        print("📥 RAW REQUEST:", request.data, flush=True)

        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        print("✅ USER TEXT:", user_text, flush=True)
        print("🔑 OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"), flush=True)
        print("🔑 GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), flush=True)

        # OpenAI Chat API (v1.0.0以降)
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}]
        )
        reply_text = response.choices[0].message.content.strip()
        print("🤖 ChatGPT 応答:", reply_text, flush=True)

        # Google Cloud TTS
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        print("✅ 音声ファイル生成:", output_path, flush=True)

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("⚠️ 全体の処理エラー:", str(e), flush=True)
        return jsonify({"reply": "エラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
