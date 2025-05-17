import os
import json
from flask import Flask, request, jsonify, render_template, send_file
from google.cloud import texttospeech
from openai import OpenAI
import dotenv
from datetime import datetime

dotenv.load_dotenv()
app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
client = OpenAI(api_key=openai_api_key)

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
        user_input = data.get("text", "").strip()
        if len(user_input) > 100:
            return jsonify({"reply": "入力は100文字以内にしてください。"}), 400

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは心優しいアシスタントです。返答は200文字以内の簡潔な日本語でお願いします。"},
                {"role": "user", "content": user_input}
            ]
        )
        reply = completion.choices[0].message.content.strip()
        if len(reply) > 200:
            reply = reply[:200]

        # 音声合成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        with open("static/output.mp3", "wb") as out:
            out.write(response.audio_content)

        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} ユーザー: {user_input}\n")
            f.write(f"{datetime.now()} みまくん: {reply}\n\n")

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"エラーが発生しました: {str(e)}"}), 500

@app.route("/logs")
def view_logs():
    try:
        with open("chatlog.txt", "r", encoding="utf-8") as f:
            logs = f.read()
        return f"<pre>{logs}</pre><br><a href='/download-log'>ログをダウンロード</a>"
    except FileNotFoundError:
        return "ログファイルが見つかりません。"

@app.route("/download-log")
def download_log():
    return send_file("chatlog.txt", as_attachment=True)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
