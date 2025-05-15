
import os
import json
from flask import Flask, render_template, request, jsonify
from google.cloud import texttospeech
from openai import OpenAI
from pathlib import Path
import dotenv

# .env の読み込み
dotenv.load_dotenv()

app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
assert openai_api_key, "OpenAI API key is not set"
assert google_application_credentials, "Google Cloud credentials are not set"

openai_client = OpenAI(api_key=openai_api_key)

# 会社・製品FAQ（簡易ルール）
faq_responses = {
    "ロボスタディ": "ロボ・スタディ株式会社は、高齢者の孤独や孤独死の問題解決を目指して、AI対話ロボット『AI・みまくん』を開発しています。",
    "会社概要": "当社は2018年に設立され、浜松市に本社を構えています。詳細は https://robostudy.jp をご覧ください。",
    "みまくん": "『AI・みまくん』は高齢者の孤独感を軽減し、日常生活を支援するための見守り対話ロボットです。",
    "価格": "『AI・みまくん』の価格は198,000円（税込）です。サブスク（月額4,200円）もあります。法人向けは別途管理費がかかります。",
    "購入方法": "ご購入はWebサイト（https://robostudy.jp）またはメール mitsunorif@robostudy.jp までご連絡ください。"
}

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

        # FAQ自動応答
        for keyword, answer in faq_responses.items():
            if keyword in user_text:
                return jsonify({"reply": answer})

        # ChatGPT 応答
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは老人を元気づける日本語を話す心優しいアシスタントです。"},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message.content.strip()

        # 音声合成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        if not os.path.exists("static"):
            os.makedirs("static")
        output_path = os.path.join("static", "output.mp3")
        with open(output_path, "wb") as out:
            out.write(tts_response.audio_content)

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("⚠️ Error:", str(e), flush=True)
        return jsonify({"reply": "エラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
