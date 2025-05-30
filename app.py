import os
import uuid
from flask import Flask, Blueprint, render_template, request, jsonify
import openai
from google.cloud import texttospeech

# ——————————————
# 環境変数の読み込み
# ・OPENAI_API_KEY
# ・GOOGLE_APPLICATION_CREDENTIALS（サービスアカウント JSON のパス）
# ——————————————
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Google TTS クライアント
tts_client = texttospeech.TextToSpeechClient()

# ——————————————
# Blueprint：日本語版
# ——————————————
ja_bp = Blueprint(
    "ja", __name__,
    url_prefix="",                 # ルート "/"
    template_folder="templates/ja" # templates/ja/chatbot.html を参照
)
@ja_bp.route("/")
def index_ja():
    return render_template("chatbot.html")

# ——————————————
# Blueprint：英語版
# ——————————————
en_bp = Blueprint(
    "en", __name__,
    url_prefix="/en",              # "/en/"
    template_folder="templates/en" # templates/en/chatbot.html を参照
)
@en_bp.route("/")
def index_en():
    return render_template("chatbot.html")

# Blueprint 登録
app.register_blueprint(ja_bp)
app.register_blueprint(en_bp)

# ——————————————
# API エンドポイント：チャット＆TTS
# ——————————————
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    user_msg = data.get("message", "")

    # 1) OpenAI へ問い合わせ
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content": user_msg}],
        max_tokens=150,
        temperature=0.7,
    )
    bot_text = resp.choices[0].message.content.strip()

    # 2) Google TTS 合成
    synthesis_input = texttospeech.SynthesisInput(text=bot_text)
    voice_params = texttospeech.VoiceSelectionParams(
        language_code="ja-JP",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    tts_res = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice_params,
        audio_config=audio_config
    )

    # 3) ファイル保存（static 以下を想定）
    fname = f"tts_{uuid.uuid4().hex}.mp3"
    out_path = os.path.join("static", fname)
    with open(out_path, "wb") as f:
        f.write(tts_res.audio_content)

    # 4) JSON で返却
    return jsonify({
        "response": bot_text,
        "audio_url": f"/static/{fname}"
    })

# ——————————————
# サーバ起動
# ——————————————
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
