from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import os
import openai
import traceback
import json
from dotenv import load_dotenv
from google.cloud import texttospeech
from google.oauth2 import service_account

load_dotenv()

# Google Cloud TTS 認証情報をJSON環境変数から読み込む
creds_info = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
credentials = service_account.Credentials.from_service_account_info(creds_info)
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

# 環境変数確認ログ
print("=========== 環境変数確認 ===========")
print("GOOGLE_CREDENTIALS_JSON is set:", os.getenv("GOOGLE_CREDENTIALS_JSON") is not None, flush=True)
print("=========== END ===========")

# OpenAI APIキー設定
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
        if not text:
            return jsonify({"error": "No text provided"}), 400

        client = tts_client
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
        return jsonify({"error": str(e)}), 500

# 動作チェック用
@app.route("/check-openai")
def check_openai():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "こんにちは"}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"❌ エラー: {str(e)}"

# ✅ アプリ起動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
