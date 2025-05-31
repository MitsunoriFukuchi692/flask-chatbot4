import os
import uuid
from flask import Flask, render_template, request, jsonify
import openai
from google.cloud import texttospeech

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__,
            static_folder="static",
            template_folder="templates")

# ── 日本語トップ ──
@app.route("/", methods=["GET"])
def index_ja():
    return render_template("ja/index.html")

# ── 英語トップ（トレーリングスラッシュあり・なしに対応） ──
@app.route("/en", methods=["GET"])
@app.route("/en/", methods=["GET"])
def index_en():
    return render_template("en/index.html")

# ── 日本語用チャットUI ──
@app.route("/chatbot", methods=["GET"])
@app.route("/chatbot/", methods=["GET"])
def chatbot_ja():
    return render_template("ja/chatbot.html")

# ── 英語用チャットUI（同じくスラッシュ対応） ──
@app.route("/chatbot_en", methods=["GET"])
@app.route("/chatbot_en/", methods=["GET"])
def chatbot_en():
    return render_template("en/chatbot.html")

# ── AJAX POST の本体ロジック ──
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("message", "")
    # デフォルトは日本語（"ja"）、英語の場合は "en" を送ってください
    lang = data.get("lang", "ja")

    # 1) OpenAI ChatCompletion 呼び出し
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_text}
        ]
    )
    reply_text = completion.choices[0].message.content

    # 2) Google TTS 呼び出し
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=reply_text)
    voice = texttospeech.VoiceSelectionParams(
        # "ja" なら日本語、"en" なら英語
        language_code="ja-JP" if lang == "ja" else "en-US",
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

    # 3) MP3 ファイルを static/audio/ 配下に保存
    audio_dir = os.path.join(app.static_folder, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(audio_dir, filename)
    with open(audio_path, "wb") as f:
        f.write(tts_response.audio_content)

    # 4) クライアントへテキストと音声 URL を返却
    return jsonify({
        "text": reply_text,
        "audio_url": f"/static/audio/{filename}"
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
