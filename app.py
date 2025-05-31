import os
import uuid
from flask import Flask, render_template, request, jsonify
import openai
from google.cloud import texttospeech

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__,
            static_folder="static",
            template_folder="templates")

# 日本語トップページ
@app.route("/", methods=["GET"])
def index_ja():
    return render_template("ja/index.html")

# 英語トップページ
@app.route("/en", methods=["GET"])
def index_en():
    return render_template("en/index.html")

# 日本語用チャットUI（iframeの中身）
@app.route("/chatbot", methods=["GET"])
def chatbot_ja():
    # templates/ja/chatbot.html を返す
    return render_template("ja/chatbot.html")

# 英語用チャットUI
@app.route("/chatbot_en", methods=["GET"])
def chatbot_en():
    # templates/en/chatbot.html を返す
    return render_template("en/chatbot.html")

# AJAX POST を受ける本体ロジック
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("message", "")
    lang = data.get("lang", "ja")

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_text}
        ]
    )
    reply_text = completion.choices[0].message.content

    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=reply_text)
    voice = texttospeech.VoiceSelectionParams(
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

    audio_dir = os.path.join(app.static_folder, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(audio_dir, filename)
    with open(audio_path, "wb") as f:
        f.write(tts_response.audio_content)

    return jsonify({
        "text": reply_text,
        "audio_url": f"/static/audio/{filename}"
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
