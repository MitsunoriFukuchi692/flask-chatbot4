import os
from flask import Flask, request, jsonify, render_template
from google.cloud import texttospeech
from dotenv import load_dotenv
import openai

# 環境変数読み込み
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("text", "")

    print("受け取ったテキスト:", user_text)

    # ChatGPT 応答取得
    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}]
    )
    response_text = chat_response.choices[0].message["content"]
    print("生成された応答:", response_text)

    # Google Cloud TTS で音声生成
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=response_text)
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

    # MP3 保存
    output_path = os.path.join("static", "output.mp3")
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    # 応答返却
    return jsonify({"response_text": response_text})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
