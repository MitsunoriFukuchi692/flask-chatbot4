from flask import Flask, request, jsonify
import openai
import os
from google.cloud import texttospeech
from dotenv import load_dotenv

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>音声チャットボット</title>
</head>
<body>
    <h1>音声チャットボット</h1>
    <p>メッセージを入力してください:</p>
    <textarea id="userInput" rows="3" cols="40">こんにちは、元気ですか？</textarea><br>
    <button onclick="sendText()">送信して音声再生</button>

    <h3>ChatGPTの返答：</h3>
    <div id="responseText" style="font-size: 1.2em;"></div>
    <br>
    <audio id="audioPlayer" controls></audio>

    <script>
        function sendText() {
            const userInput = document.getElementById("userInput").value;

            fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ text: userInput })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("responseText").innerText = data.response_text;
                const audio = document.getElementById("audioPlayer");
                audio.src = "/static/output.mp3?ts=" + new Date().getTime();
                audio.play();
            });
        }
    </script>
</body>
</html>
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data["text"]

    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}]
    )
    response_text = chat_response.choices[0].message["content"]

    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=response_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    output_path = os.path.join("static", "output.mp3")
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    return jsonify({"response_text": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
