import os
from flask import Flask, request, jsonify, render_template, send_file
from google.cloud import texttospeech
import openai

app = Flask(__name__)

# 環境変数の確認（Renderで設定済みの前提）
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot.html")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data["text"]
    print("受け取ったテキスト:", user_text)

    # ChatGPTへ送信
    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}]
    )
    response_text = chat_response.choices[0].message["content"]

    # Google TTSで音声生成
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=response_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    output_path = os.path.join("static", "output.mp3")
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    return jsonify({"response_text": response_text})

# ローカルテスト用（Renderでは不要）
# if __name__ == "__main__":
#     app.run(debug=False, host="0.0.0.0", port=10000)
