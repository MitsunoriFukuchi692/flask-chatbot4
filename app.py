import os
import json
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
from pathlib import Path
import dotenv
import openai

# .env 読み込み
dotenv.load_dotenv()

# Flask アプリ初期化
app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

# レート制限
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

# Google Cloud 認証
google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not google_credentials_path or not Path(google_credentials_path).exists():
    raise FileNotFoundError("Google Cloud 認証ファイルが見つかりません。")

# OpenAI キー設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# 会話ログ保存ファイル
chatlog_path = Path("chatlog.txt")

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        if len(user_text) > 100:
            return jsonify({"reply": "みまくん: 申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"}), 200

        messages = [
            {"role": "system", "content": "あなたは老人にやさしく応答する日本語のアシスタントです。"},
            {"role": "user", "content": user_text}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )

        reply_text = response.choices[0].message.content.strip()

        # 音声生成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        output_dir = Path("static")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "output.mp3"
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        # ログ保存
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        with open(chatlog_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp} USER: {user_text}\n{timestamp} BOT: {reply_text}\n\n")

        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"reply": f"みまくん: エラーが発生しました ({str(e)})"}), 500

@app.route("/logs", methods=["GET"])
def get_logs():
    if chatlog_path.exists():
        return send_file(chatlog_path, mimetype="text/plain", as_attachment=False)
    return "ログが存在しません", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
