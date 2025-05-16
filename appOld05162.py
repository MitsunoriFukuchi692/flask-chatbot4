
import os
import json
from flask import Flask, render_template, request, jsonify
from google.cloud import texttospeech
from pathlib import Path
from openai import OpenAI
import dotenv

app = Flask(__name__)
config = dotenv.dotenv_values(".env")
openai_client = OpenAI(api_key=config["OPENAI_API_KEY"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = json.loads(request.data)
        user_text = data.get("text", "").strip()
        print("User input:", user_text)

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは心優しく高齢者に寄り添う日本語のアシスタントです。会社や製品に関する質問にはロボ・スタディ株式会社とAI・みまくんに限定して答えてください。"},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message.content.strip()
        print("Response:", reply_text)

        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        if not os.path.exists("static"):
            os.makedirs("static")
        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        return jsonify({"reply": reply_text, "audio_url": "/static/output.mp3"})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"reply": "エラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
