import os
import json
import logging           # 例外ログ出力用

# 標準出力に DEBUG レベル以上のログを出力
logging.basicConfig(level=logging.DEBUG)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
import openai

# Flask アプリ初期化
app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

# レート制限（1分間に10リクエスト）
limiter = Limiter(app, key_func=get_remote_address, default_limits=["10 per minute"])

# APIキーの読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

# 静的 .html にアクセスする場合も、同じテンプレートを返す
@app.route("/chatbot.html")
def chatbot_html():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("3 per 10 seconds")  # 連打防止（10秒に3回まで）
def chat():
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        # 入力文字数制限
        if len(user_text) > 100:
            return jsonify({
                "reply": "みまくん: 申し訳ありませんが、メッセージは100文字以内でお願いいたします。再度短くして送信してください。"
            }), 400

        # OpenAI 応答生成
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは親切な日本語のアシスタントです。"},
                {"role": "user",   "content": user_text}
            ]
        )
        reply_text = response.choices[0].message["content"].strip()
        if len(reply_text) > 200:
            reply_text = reply_text[:197] + "..."

        # Google Cloud TTS による音声合成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        tts_response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # static/output.mp3 に保存
        os.makedirs("static", exist_ok=True)
        with open("static/output.mp3", "wb") as out:
            out.write(tts_response.audio_content)

        # チャットログ保存
        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(f"ユーザー: {user_text}\nみまくん: {reply_text}\n---\n")

        return jsonify({"reply": reply_text})

    except Exception as e:
        logging.exception("Unhandled exception in /chat")
        return jsonify({"reply": "みまくん: 内部エラーが発生しました。もう一度お試しください。"}), 500

@app.route("/logs")
def logs():
    try:
        with open("chatlog.txt", "r", encoding="utf-8") as f:
            log_content = f.read()
        return f"<pre>{log_content}</pre><a href='/download-logs'>ログをダウンロード</a>"
    except FileNotFoundError:
        return "ログファイルが存在しません。"

@app.route("/download-logs")
def download_logs():
    return open("chatlog.txt", "rb").read(), 200, {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': 'attachment; filename="chatlog.txt"'
    }

if __name__ == "__main__":
    # 開発用サーバー起動（本番は gunicorn 推奨）
    app.run(host="0.0.0.0", port=10000)
