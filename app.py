
import os
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from datetime import datetime
import json
from openai import OpenAI
from google.cloud import texttospeech

app = Flask(__name__)
CORS(app)  # CORS対応

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_text = data.get("text", "").strip()
        if not user_text:
            return jsonify({"reply": "メッセージが空です。"}), 400

        # ChatGPT 応答生成
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは親切で丁寧な会社案内チャットボットです。"},
                {"role": "user", "content": user_text}
            ]
        )
        reply = response.choices[0].message.content.strip()

        # Google TTS 音声生成
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply)
        voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        os.makedirs("static", exist_ok=True)
        with open("static/output.mp3", "wb") as out:
            out.write(tts_response.audio_content)

        # ログ保存
        with open("chatlog.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ユーザー: {user_text}\nみまくん: {reply}\n\n")

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"エラーが発生しました: {str(e)}"}), 500

@app.route("/logs")
def view_logs():
    try:
        with open("chatlog.txt", "r", encoding="utf-8") as f:
            log_content = f.read()
        return f"<pre>{log_content}</pre><br><a href='/download-logs'>📥 ログをダウンロード</a>"
    except Exception as e:
        return f"ログ読み込みエラー: {str(e)}"

@app.route("/download-logs")
def download_logs():
    return send_file("chatlog.txt", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
