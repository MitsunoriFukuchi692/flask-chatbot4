
import os
import json
from flask import Flask, request, jsonify, render_template, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from google.cloud import texttospeech
from dotenv import load_dotenv

# .envの読み込み
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

# レート制限（例：1分に10回まで）
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

# OpenAIとGoogle TTSのキー取得
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
assert OPENAI_API_KEY and GOOGLE_APPLICATION_CREDENTIALS

from openai import OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/")
def index():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    try:
        user_input = request.json.get("text", "").strip()
        if len(user_input) > 100:
            return jsonify({"reply": "申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"})

        # ChatGPT API呼び出し
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは親切な高齢者支援アシスタントです。"},
                {"role": "user", "content": user_input}
            ]
        )
        reply_text = response.choices[0].message.content.strip()[:200]  # 応答も200文字以内
        log_entry = f"User: {user_input}\nBot: {reply_text}\n\n"
        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)

        # 音声合成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        output_path = "static/output.mp3"
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        return jsonify({"reply": reply_text})
    except Exception as e:
        print("❌ エラー:", str(e))
        return jsonify({"reply": "みまくん: エラーが発生しました。"}), 500

@app.route("/logs")
def logs():
    return send_file("chatlog.txt", as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
