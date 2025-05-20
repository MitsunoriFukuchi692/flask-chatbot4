import os
import json
import logging    # 例外ログ出力用

# 開発中は DEBUG、運用時は INFO などに変更してください
logging.basicConfig(level=logging.INFO)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
import openai
from markupsafe import escape   # ← 追加

# Flask アプリ初期化
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, origins=["https://robostudy.jp"])

# レート制限（1 分間に 10 リクエスト）
limiter = Limiter(app, key_func=get_remote_address, default_limits=["10 per minute"])

# 環境変数から API キー読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


@app.route("/")
def index():
    return render_template("index.html")


# /chatbot および /chatbot.html の両方に対応
@app.route("/chatbot")
@app.route("/chatbot.html")
def chatbot():
    return render_template("chatbot.html")


# デバッグ用：chatbot.html の配置場所を一覧表示
@app.route("/debug/chatbot-files")
def debug_chatbot_files():
    try:
        base_dir = os.path.dirname(__file__)
        found = []
        for root, dirs, files in os.walk(base_dir):
            if "chatbot.html" in files:
                rel = os.path.relpath(os.path.join(root, "chatbot.html"), base_dir)
                found.append(rel)
        return "<br>".join(found) if found else "no chatbot.html here"
    except Exception:
        logging.exception("Error in debug_chatbot_files")
        return "error listing files", 500


# チャット API エンドポイント
@app.route("/chat", methods=["POST"])
@limiter.limit("3 per 10 seconds")  # 10 秒間に 3 回まで
def chat():
    try:
        # JSON ボディを読み込み
        data = json.loads(request.data)
        raw = data.get("message", "")     # 生の入力
        user_text = escape(raw).strip() # XSS 対策としてサニタイズ＋前後空白除去

        # 長すぎるメッセージは弾く
        if len(user_text) == 0:
            return jsonify({"reply": "⚠️ メッセージが空です"}), 400
        if len(user_text) > 100:
            return jsonify({"reply": "⚠️ メッセージは100文字以内でお願いします。"}), 400

        # ChatGPT（gpt-4o）へ問い合わせ
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
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_resp = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # 音声ファイルを static/output.mp3 に書き出し
        os.makedirs(app.static_folder, exist_ok=True)
        out_path = os.path.join(app.static_folder, "output.mp3")
        with open(out_path, "wb") as out:
            out.write(tts_resp.audio_content)

        # ログ保存
        log_line = f"ユーザー: {user_text}\nみまくん: {reply_text}\n---\n"
        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(log_line)

        return jsonify({"reply": reply_text})
    except Exception:
        logging.exception("Unhandled exception in /chat")
        return jsonify({"reply": "⚠️ 内部エラーが発生しました。"}), 500


# チャットログを画面表示
@app.route("/logs")
def logs():
    try:
        with open("chatlog.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return f"<pre>{content}</pre><a href='/download-logs'>ログをダウンロード</a>"
    except FileNotFoundError:
        return "ログファイルが存在しません。"


# チャットログをファイルとしてダウンロード
@app.route("/download-logs")
def download_logs():
    return (
        open("chatlog.txt", "rb").read(),
        200,
        {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': 'attachment; filename="chatlog.txt"'
        }
    )


if __name__ == "__main__":
    # 本番では gunicorn 等を使うことを推奨
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
