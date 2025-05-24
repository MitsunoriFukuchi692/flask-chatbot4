import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import io

# 環境変数読み込み
openai_api_key = os.getenv("OPENAI_API_KEY")
supabase_url     = os.getenv("SUPABASE_URL")
supabase_key     = os.getenv("SUPABASE_KEY")
google_creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

# Flask アプリ初期化
app = Flask(
    __name__,
    static_folder="static",         # 静的ファイル格納フォルダ
    template_folder="templates"     # テンプレート格納フォルダ
)
# 本番サイトとローカルを許可
CORS(app, origins=["https://robostudy.jp", "http://localhost:5000"])


def call_openai(user_text: str) -> str:
    """
    TODO: OpenAI API 呼び出しを実装してください。
    例:
      import openai
      openai.api_key = openai_api_key
      resp = openai.ChatCompletion.create(...)
      return resp.choices[0].message.content
    """
    return "ここにAIの応答が入ります"


def synthesize_speech(text: str) -> bytes:
    """
    TODO: Google Cloud Text-to-Speech を呼び出し、MP3 バイト列を返してください。
    例:
      from google.cloud import texttospeech
      creds = json.loads(google_creds_json)
      client = texttospeech.TextToSpeechClient.from_service_account_info(creds)
      # synthesis...
    """
    return b""


@app.route("/")
def top():
    # templates/index.html を返す
    return render_template("index.html")


@app.route("/chatbot")
def chatbot_page():
    # templates/chatbot.html を返す
    return render_template("chatbot.html")


@app.route("/speak", methods=["GET"])
def speak_page():
    # templates/speak.html を返す
    return render_template("speak.html")


@app.route("/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    user_text = data.get("text", "")
    # AI 応答取得
    bot_reply = call_openai(user_text)
    # 音声合成して static/output.mp3 に書き込む
    audio_bytes = synthesize_speech(user_text)
    out_path = os.path.join(app.static_folder, "output.mp3")
    with open(out_path, "wb") as f:
        f.write(audio_bytes)
    return jsonify({"reply": bot_reply})


@app.route("/speak", methods=["POST"])
def api_speak():
    data = request.get_json() or {}
    text = data.get("text", "")
    audio_bytes = synthesize_speech(text)
    return send_file(
        io.BytesIO(audio_bytes),
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="speech.mp3"
    )


@app.route("/debug/chatbot-files")
def debug_files():
    """
    デバッグ用: templates フォルダ内のファイル一覧を返す
    """
    file_list = []
    for root, dirs, files in os.walk(app.template_folder):
        for file in files:
            rel = os.path.relpath(os.path.join(root, file), app.template_folder)
            file_list.append(rel)
    return jsonify(file_list)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
