import os
import json
from flask import Flask, render_template, request, jsonify, send_file, Response
from google.cloud import texttospeech
import dotenv
from pathlib import Path
from openai import OpenAI

# .env 読み込み
dotenv.load_dotenv()
config = dotenv.dotenv_values(Path(".env"))

app = Flask(__name__)

# OpenAIとGoogle Cloudの認証情報取得
openai_api_key = os.getenv("OPENAI_API_KEY")
google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
assert openai_api_key, "OpenAI API key is missing."
assert google_application_credentials, "Google Cloud credentials missing."

# OpenAI client初期化
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
        data = request.get_json()
        user_text = data.get("text", "").strip()

        # ChatGPT 応答生成
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは高齢者を元気づける、親切な日本語アシスタントです。"},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message.content.strip()

        # Google TTSで音声合成
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

        # ログ記録
        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(f"User: {user_text}\nBot: {reply_text}\n\n")

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("⚠️ エラー:", str(e))
        return jsonify({"reply": "エラーが発生しました。"}), 500

@app.route("/logs")
def view_logs():
    allowed_ip = "127.0.0.1"
    if request.remote_addr != allowed_ip:
        return "アクセスが許可されていません", 403

    if not os.path.exists("chatlog.txt"):
        return "ログファイルが存在しません。"

    with open("chatlog.txt", "r", encoding="utf-8") as file:
        log_content = file.read()

    html = f"""
    <html>
        <head><title>チャットログ表示</title></head>
        <body>
            <h2>チャットログ</h2>
            <pre>{log_content}</pre>
            <a href="/download_log" download>
                <button>ログをダウンロード</button>
            </a>
        </body>
    </html>
    """
    return Response(html, mimetype="text/html")

@app.route("/download_log")
def download_log():
    if request.remote_addr != "127.0.0.1":
        return "アクセスが許可されていません", 403
    return send_file("chatlog.txt", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
