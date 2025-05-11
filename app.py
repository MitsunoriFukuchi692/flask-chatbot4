import os
import io
from flask import Flask, request, jsonify, render_template, Response, send_file
from google.cloud import texttospeech
import openai

app = Flask(__name__)

# 環境変数からAPIキーを読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("text", "")
    print("受け取ったテキスト:", user_text)

    # ChatGPT にテキスト送信
    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}]
    )
    response_text = chat_response.choices[0].message["content"]
    return jsonify({"response_text": response_text})

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return "No text provided", 400

    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    return Response(response.audio_content, mimetype="audio/mpeg")

# Render 用：外部ポート対応
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
