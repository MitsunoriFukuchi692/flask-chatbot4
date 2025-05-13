

import os
import json
from flask import Flask, render_template, request, jsonify
from google.cloud import texttospeech
#import openai
import dotenv
#from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
secret_fullpath = Path('/etc/secrets/.env')

# .envファイルから環境変数を読み込み
config = dotenv.dotenv_values(secret_fullpath)

app = Flask(__name__)

# OpenAI APIキーとGoogle Cloud認証情報の読み込み
openai_api_key = os.getenv("OPENAI_API_KEY")
assert openai_api_key, "OpenAI API key is not set in environment variables."
#openai.api_key_path = os.getenv("OPENAI_API_KEY_PATH")
#assert openai.api_key_path, "OpenAI API key path is not set in environment variables."
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
assert google_application_credentials, "Google Cloud credentials are not set in environment variables."
'''credential_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not Path(credential_path).exists():
        raise FileNotFoundError(f"Google Cloud credentials file not found: {credential_path}")  '''

# Create an OpenAI object with a specific API key
openai_client = OpenAI(api_key=config["OPENAI_API_KEY"])

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

        # Use the client to make API calls
        '''response = openai_client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}]
        )'''

        # OpenAI Chat API (v1.0.0以降)
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini", # 3.5-turbo",
            messages=[{"role": "system", "content": "あなたは老人を元気づける日本語を話す心優しいアシスタントです。"},
                {"role": "user", "content": user_text}]
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
        if not os.path.exists("static"):
            os.makedirs("static")  
            print("✅ staticフォルダを作成しました。", flush=True)
        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        # print("✅ 音声ファイル生成:", output_path, flush=True)
        file_size = os.path.getsize(output_path)
        print("✅ 音声ファイルサイズ:", file_size, "bytes", flush=True) 
        return jsonify({"reply": reply_text})

    except Exception as e:
        print("⚠️ 全体の処理エラー:", str(e), flush=True)
        return jsonify({"reply": "エラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
