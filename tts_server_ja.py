from flask import Flask, request, send_file
import requests
import io
import base64

app = Flask(__name__)

GOOGLE_TTS_API_KEY = "AIzaSyDps9uNB0JuDHO_sP58rnVb5Bw_4EXv1QI"

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "")

    headers = {
        "X-Goog-Api-Key": GOOGLE_TTS_API_KEY,
        "Content-Type": "application/json; charset=utf-8",
    }
    body = {
        "input": {"text": text},
        "voice": {"languageCode": "ja-JP", "name": "ja-JP-Wavenet-B"},
        "audioConfig": {"audioEncoding": "MP3"}
    }

    r = requests.post(
        "https://texttospeech.googleapis.com/v1/text:synthesize",
        headers=headers,
        json=body
    )

    audio_content = r.json().get("audioContent")
    if not audio_content:
        return "音声生成に失敗しました", 500

    audio_bytes = io.BytesIO()
    audio_bytes.write(base64.b64decode(audio_content))
    audio_bytes.seek(0)

    return send_file(audio_bytes, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
