import os
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
import openai
import stripe

# ログ設定
logging.basicConfig(level=logging.DEBUG)

# Flask アプリ初期化
app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])
limiter = Limiter(app, key_func=get_remote_address, default_limits=["10 per minute"])

# 環境変数から各種キーを読み込む
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ルート：トップページ（index.html）を返す
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# 既存チャットボット用エンドポイント
@app.route("/chat", methods=["POST"])
@limiter.limit("3 per 10 seconds")
def chat():
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()
        if len(user_text) > 100:
            return jsonify({"reply": "みまくん: メッセージは100文字以内でお願いします。"}), 400

        # ChatGPT へ送信
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

        # TTS 合成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # 音声ファイル保存
        os.makedirs("static", exist_ok=True)
        with open("static/output.mp3", "wb") as out:
            out.write(tts_response.audio_content)

        # ログ保存
        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(f"ユーザー: {user_text}\nみまくん: {reply_text}\n---\n")

        return jsonify({"reply": reply_text})

    except Exception:
        logging.exception("/chat エラー")
        return jsonify({"reply": "みまくん: 内部エラーです。再度お試しください。"}), 500

# 会話ログ表示・ダウンロード
@app.route("/logs")
def logs():
    try:
        with open("chatlog.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return f"<pre>{content}</pre><a href='/download-logs'>ログダウンロード</a>"
    except FileNotFoundError:
        return "ログが存在しません。"

@app.route("/download-logs")
def download_logs():
    return (
        open("chatlog.txt", "rb").read(),
        200,
        {
            "Content-Type": "application/octet-stream",
            "Content-Disposition": 'attachment; filename="chatlog.txt"',
        },
    )

# ——— 追加機能：インボイス発行 ———
@app.route("/create_invoice", methods=["POST"])
def create_invoice():
    # 1) 顧客を作成
    customer = stripe.Customer.create(
        email="test@example.com",
        name="テスト顧客"
    )
    # 2) 請求アイテムを登録（¥1,300）
    stripe.InvoiceItem.create(
        customer=customer.id,
        amount=1300,
        currency="jpy",
        description="デモ請求"
    )
    # 3) インボイスを作成＆確定
    invoice = stripe.Invoice.create(customer=customer.id)
    invoice = stripe.Invoice.finalize_invoice(invoice.id)
    # 4) 支払いページへリダイレクト
    return redirect(invoice.hosted_invoice_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
