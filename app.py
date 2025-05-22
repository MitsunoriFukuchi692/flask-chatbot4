import os
import json
import logging  # 例外ログ出力用

# ロギング設定: 標準出力に DEBUG レベル以上を出力
logging.basicConfig(level=logging.DEBUG)

# Flask インポートを明示的に追加
from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
import openai

# Flask アプリ初期化
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)
CORS(app, origins=["https://robostudy.jp"])

# レート制限設定: 1分間に10リクエストまで
limiter = Limiter(app, key_func=get_remote_address, default_limits=["10 per minute"])

# 環境変数から API キー読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

@app.route("/")
def index():
    return render_template("index.html")

# /chatbot, /chatbot.html で同じテンプレートを返却（キャッシュ無効化付き）
@app.route("/chatbot")
@app.route("/chatbot.html")
def chatbot():
    resp = make_response(render_template("chatbot.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# 全レスポンスにキャッシュ無効化ヘッダーを付与
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# デバッグ用: プロジェクト内の chatbot.html 一覧を返す
@app.route("/debug/chatbot-files")
def debug_chatbot_files():
    try:
        base_dir = os.path.dirname(__file__)
        found = []
        for root, dirs, files in os.walk(base_dir):
            if "chatbot.html" in files:
                found.append(os.path.relpath(os.path.join(root, "chatbot.html"), base_dir))
        return "<br>".join(found) if found else "no chatbot.html here"
    except Exception:
        logging.exception("Error in debug_chatbot_files")
        return "error listing files", 500

# チャット API エンドポイント\@@lint
@app.route("/chat", methods=["POST"])
@limiter.limit("3 per 10 seconds")  # 連打防止
def chat():
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        if len(user_text) > 100:
            return jsonify({"reply": "みまくん: メッセージは100文字以内でお願いします。"}), 400

        # OpenAI で応答生成
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

        # Google Cloud TTS
        tts_client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_resp = tts_client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

        # 音声ファイル出力
        os.makedirs("static", exist_ok=True)
        with open("static/output.mp3", "wb") as out:
            out.write(tts_resp.audio_content)

        # テキストログ保存
        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(f"ユーザー: {user_text}\nみまくん: {reply_text}\n---\n")

        return jsonify({"reply": reply_text})
    except Exception:
        logging.exception("Unhandled exception in /chat")
        return jsonify({"reply": "みまくん: 内部エラーが発生しました。"}), 500

# ログ表示エンドポイント
@app.route("/logs")
def logs():
    try:
        with open("chatlog.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return f"<pre>{content}</pre><a href='/download-logs'>ログをダウンロード</a>"
    except FileNotFoundError:
        return "ログファイルが存在しません。"

# ログダウンロード
def download_logs():
    return open("chatlog.txt", "rb").read(), 200, {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": 'attachment; filename="chatlog.txt"'
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
