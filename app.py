import os
from flask import Flask, request, jsonify, render_template
import openai
from google.cloud import texttospeech
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# APIキー読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    print("📥 RAW REQUEST:", request.data, flush=True)

    try:
        data = request.get_json()
        user_text = data.get("text", "")

        print("✅ USER TEXT:", user_text, flush=True)
        print("🔑 OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"), flush=True)
        print("🔑 GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), flush=True)

        # OpenAI から応答生成
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切な日本語のアシスタントです。"},
                {"role": "user", "content": user_text}
            ]
        )
        response_text = response['choices'][0]['message']['content'].strip()
        print("🤖 OpenAI 応答:", response_text, flush=True)

        # Google Cloud TTS 音声合成
        try:
            tts_client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=response_text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="ja-JP",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

            tts_response = tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            # 音声ファイルの保存
            output_path = os.path.join("static", "output.mp3")
            with open(output_path, "wb") as out:
                out.write(tts_response.audio_content)
            print("✅ 音声ファイルを保存しました:", output_path, flush=True)

        except Exception as e:
            print("❌ 音声ファイル生成エラー:", e, flush=True)
            return jsonify({"response_text": "音声の生成に失敗しました。"}), 500

        return jsonify({"response_text": response_text})

    except Exception as e:
        print("🚨 全体の処理エラー:", str(e), flush=True)
        return jsonify({"response_text": "エラーが発生しました。"}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
