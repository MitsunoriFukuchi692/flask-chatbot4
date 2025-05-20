import os
import json
import logging

# 開発用はDEBUG、本番用はINFO等に変更可能
logging.basicConfig(level=logging.INFO)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from google.cloud import texttospeech
import openai
from markupsafe import escape
from pdf_content import company_info, product_info  # 同ディレクトリに配置

# Flaskアプリケーション初期化
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, origins=["https://robostudy.jp"])

# レート制限設定（例: 1分間に10リクエスト）
limiter = Limiter(app, key_func=get_remote_address, default_limits=["10 per minute"])

# 環境変数からAPIキー読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
@app.route("/chatbot.html")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("3 per 10 seconds")  # 10秒間に3回まで
def chat():
    try:
        data = request.get_json() or {}
        raw = data.get("message", "")
        user_text = escape(raw).strip()

        # キーワードマッチで固定レスポンス
        triggers = {
            ("会社について", "ロボスタディについて", "ロボ・スタディについて"): company_info,
            ("みまくんについて", "AIみまくんについて", "ロボットについて"):      product_info,
        }
        for keys, resp in triggers.items():
            if any(k in user_text for k in keys):
                return jsonify({"reply": resp})

        # 空文字チェック
        if not user_text:
            return jsonify({"reply": "⚠️ メッセージが空です"}), 400

        # OpenAI ChatCompletion 呼び出し
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切な日本語のアシスタントです。"},
                {"role": "user",   "content": user_text}
            ]
        )
        reply = response.choices[0].message["content"].strip()

        # TTS (Google Cloud Text-to-Speech)
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_resp = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        
        # 音声ファイル書き出し
        os.makedirs(app.static_folder, exist_ok=True)
        with open(os.path.join(app.static_folder, "output.mp3"), "wb") as f:
            f.write(tts_resp.audio_content)

        # チャットログを保存
        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(f"ユーザー: {user_text}\nボット: {reply}\n---\n")

        return jsonify({"reply": reply})

    except Exception:
        logging.exception("Exception in /chat")
        return jsonify({"reply": "⚠️ 内部エラーが発生しました。"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
