import os
import uuid
from flask import Flask, render_template, request, jsonify
import openai
from google.cloud import texttospeech

# OpenAI API キーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# Flask アプリの初期化
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# ── 日本語トップページ ──
@app.route("/", methods=["GET"])
def index_ja():
    return render_template("ja/index.html")


# ── 日本語チャット画面 ──
@app.route("/chatbot", methods=["GET"])
def chatbot_ja():
    return render_template("ja/chatbot.html")


# ── 日本語 About ページ ──
@app.route("/about", methods=["GET"])
def about_ja():
    return render_template("ja/about.html")


# ── 日本語 Products ページ ──
@app.route("/products", methods=["GET"])
def products_ja():
    return render_template("ja/products.html")


# ── 日本語 Services ページ ──
@app.route("/services", methods=["GET"])
def services_ja():
    return render_template("ja/services.html")


# ── 日本語 Contact ページ ──
@app.route("/contact", methods=["GET"])
def contact_ja():
    return render_template("ja/contact.html")


# ── チャット用エンドポイント ──
@app.route("/chat", methods=["POST"])
def chat():
    """
    フロントエンドから受け取った JSON で共通の "message" キーを取り出し、
    OpenAI ChatCompletion API に投げて返答テキストを取得。
    さらに Google Text-to-Speech で MP3 を生成し、クライアントに返す JSON を組み立てる。
    """
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # 1) OpenAI へ ChatCompletion をリクエスト
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切なアシスタントです。"},
                {"role": "user", "content": user_message}
            ]
        )
        ai_text = completion.choices[0].message.content.strip()
    except Exception as e:
        return jsonify({"error": f"OpenAI request failed: {str(e)}"}), 500

    # 2) Google TTS で音声ファイルを生成
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=ai_text)
        # 日本語の音声設定
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        # MP3 ファイル名をユニークに生成し、static/audio フォルダに保存
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        audio_dir = os.path.join(app.static_folder, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        file_path = os.path.join(audio_dir, filename)
        with open(file_path, "wb") as out_file:
            out_file.write(response.audio_content)
        audio_url = f"/static/audio/{filename}"
    except Exception as e:
        return jsonify({"error": f"TTS synthesis failed: {str(e)}"}), 500

    # 3) クライアントに JSON で返却
    return jsonify({
        "text": ai_text,
        "audio_url": audio_url
    })


# ── 英語トップページ ──
@app.route("/en", methods=["GET"])
def index_en():
    return render_template("en/index.html")


# ── 英語チャット画面 ──
@app.route("/en/chatbot_en", methods=["GET"])
def chatbot_en():
    return render_template("en/chatbot.html")


# ── 英語 About ページ ──
@app.route("/en/about", methods=["GET"])
def about_en():
    return render_template("en/about.html")


# ── 英語 Products ページ ──
@app.route("/en/products", methods=["GET"])
def products_en():
    return render_template("en/products.html")


# ── 英語 Services ページ ──
@app.route("/en/services", methods=["GET"])
def services_en():
    return render_template("en/services.html")


# ── 英語 Contact ページ ──
@app.route("/en/contact", methods=["GET"])
def contact_en():
    return render_template("en/contact.html")


if __name__ == "__main__":
    # Render が割り当てるポートを取得（デフォルトは 5000）
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
