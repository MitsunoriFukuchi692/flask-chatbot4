from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
import traceback
from google.cloud import texttospeech

from dotenv import load_dotenv
load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

tts_client = texttospeech.TextToSpeechClient()

# 🌐 環境変数確認（Renderログで確認用）
print("=========== 環境変数確認 ===========")
print("GOOGLE_APPLICATION_CREDENTIALS =", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"), flush=True)
print("=========== END ===========")

# 🔧 OpenAI APIキー
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Flaskアプリ設定
app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "https://robostudy.jp"}})

# 💬 Chatエンドポイント
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切なアシスタントです。"},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)})

# 🔊 音声読み上げエンドポイント（Google TTS）
@app.route("/speak", methods=["POST"])
def speak():
    try:
        data = request.get_json()
        text = data.get("text", "")

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        return response.audio_content, 200, {
            'Content-Type': 'audio/mpeg',
            'Content-Disposition': 'inline; filename="output.mp3"'
        }

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)})

print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

@app.route("/")
def home():
    return "Flask chatbot is running!"

# ✅ アプリ起動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

