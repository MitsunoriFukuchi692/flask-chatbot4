import os
import json
import logging
from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
import openai

# ロギング設定
logging.basicConfig(level=logging.DEBUG)

# Flask アプリ初期化
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app, origins=["https://robostudy.jp", "http://localhost:5000"])

# レート制限設定
limiter = Limiter(app, key_func=get_remote_address, default_limits=["10 per minute"])

# 環境変数から API キー読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route("/chatbot")
@app.route("/chatbot.html")
def chatbot():
    """チャットボットページ（キャッシュ無効化付き）"""
    resp = make_response(render_template("chatbot.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# 静的ファイル配信（CSS、JS、画像、動画、PDF等）
@app.route('/<path:filename>')
def serve_static_files(filename):
    """静的ファイルの配信"""
    try:
        # セキュリティのため、一部のファイル拡張子のみ許可
        allowed_extensions = ['.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.mp4', '.pdf', '.mp3']
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext in allowed_extensions:
            return send_from_directory('.', filename)
        else:
            return "File type not allowed", 403
    except Exception as e:
        logging.error(f"Error serving file {filename}: {e}")
        return "File not found", 404

# 全レスポンスにキャッシュ無効化ヘッダーを付与
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/chat", methods=["POST"])
@limiter.limit("3 per 10 seconds")  # 連打防止
def chat():
    """チャット処理"""
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()

        if len(user_text) > 100:
            return jsonify({"reply": "みまくん: メッセージは100文字以内でお願いします。"}), 400

        # OpenAI で応答生成
        if openai.api_key:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "あなたは高齢者向けの優しいAIアシスタント「みまくん」です。親しみやすく、分かりやすい日本語で応答してください。"},
                    {"role": "user", "content": user_text}
                ]
            )
            reply_text = response.choices[0].message["content"].strip()
        else:
            # API キーがない場合のデフォルト応答
            reply_text = f"こんにちは！「{user_text}」についてお話しいただき、ありがとうございます。みまくんです。"
        
        if len(reply_text) > 200:
            reply_text = reply_text[:197] + "..."

        # Google Cloud TTS で音声生成
        try:
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
        except Exception as e:
            logging.error(f"TTS生成エラー: {e}")

        # テキストログ保存
        try:
            with open("chatlog.txt", "a", encoding="utf-8") as f:
                f.write(f"ユーザー: {user_text}\nみまくん: {reply_text}\n---\n")
        except Exception as e:
            logging.error(f"ログ保存エラー: {e}")

        return jsonify({"reply": reply_text})
        
    except Exception as e:
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
@app.route("/download-logs")
def download_logs():
    try:
        with open("chatlog.txt", "rb") as f:
            content = f.read()
        return content, 200, {
            "Content-Type": "application/octet-stream",
            "Content-Disposition": 'attachment; filename="chatlog.txt"'
        }
    except FileNotFoundError:
        return "ログファイルが存在しません。", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)