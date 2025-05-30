import os
import uuid
from flask import Flask, render_template, request, jsonify
import openai
from google.cloud import texttospeech

# 環境変数から OpenAI API キーを取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# Flask アプリの初期化
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

@app.route("/")
def index_ja():
    # templates/ja/index.html を参照
    return render_template("ja/index.html")

@app.route("/en/")
def index_en():
    # templates/en/index.html を参照
    return render_template("en/index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("message", "")
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
