
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google.cloud import texttospeech
import openai

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        print("📥 RAW REQUEST:", request.data)
        data = request.get_json(force=True)
        user_text = data.get("text", "")
        print("✅ USER TEXT:", user_text, flush=True)
        print("🔑 OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
        print("🔑 GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

        openai.api_key = os.getenv("OPENAI_API_KEY")
        chat_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切な日本語のアシスタントです。"},
                {"role": "user", "content": user_text}
            ]
        )
        response_text = chat_response.choices[0].message["content"]

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=response_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(response.audio_content)

        return jsonify({"response_text": response_text})

    except Exception as e:
        print("🛠️ 全体の処理エラー:", e)
        return jsonify({"response_text": "エラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)