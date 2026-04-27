import os
import uuid
from flask import Flask, render_template, request, jsonify
import openai
from google.cloud import texttospeech

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# ── 日本語版ルート ──

@app.route("/", methods=["GET"])
def home_ja():
    return render_template("ja/index.html")

@app.route("/about", methods=["GET"])
def about_ja():
    return render_template("ja/about.html")

@app.route("/products", methods=["GET"])
def products_ja():
    return render_template("ja/products.html")

@app.route("/services", methods=["GET"])
def services_ja():
    return render_template("ja/services.html")

@app.route("/contact", methods=["GET"])
def contact_ja():
    return render_template("ja/contact.html")

@app.route("/chatbot", methods=["GET"])
@app.route("/chatbot/", methods=["GET"])
def chatbot_ja():
    return render_template("ja/chatbot.html")

# ── 英語版ルート ──

@app.route("/en", methods=["GET"])
@app.route("/en/", methods=["GET"])
def home_en():
    return render_template("en/index.html")

@app.route("/en/about", methods=["GET"])
@app.route("/en/about/", methods=["GET"])
def about_en():
    return render_template("en/about.html")

@app.route("/en/products", methods=["GET"])
@app.route("/en/products/", methods=["GET"])
def products_en():
    return render_template("en/products.html")

@app.route("/en/services", methods=["GET"])
@app.route("/en/services/", methods=["GET"])
def services_en():
    return render_template("en/services.html")

@app.route("/en/contact", methods=["GET"])
@app.route("/en/contact/", methods=["GET"])
def contact_en():
    return render_template("en/contact.html")

@app.route("/en/chatbot_en", methods=["GET"])
@app.route("/en/chatbot_en/", methods=["GET"])
def chatbot_en():
    return render_template("en/chatbot.html")

# ── チャットボット用エンドポイント ──

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("message", "")
    lang = data.get("lang", "ja")

    # 会社ごとのプロンプトを読み込む
    company = data.get("company", "robostudy")
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", f"{company}.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    else:
        system_prompt = "You are a helpful assistant."

    # ── OpenAI ChatCompletion ──
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = completion.choices[0].message.content
    except Exception as e:
        return jsonify({"text": f"Error generating response: {e}", "audio_url": ""}), 500

    # ── Google TTS ──
    try:
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)
        if lang == "en":
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
        else:
            voice = texttospeech.VoiceSelectionParams(
                language_code="ja-JP",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        tts_response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
    except Exception as e:
        return jsonify({"text": f"Error generating TTS: {e}", "audio_url": ""}), 500

    # ── MP3保存 ──
    audio_dir = os.path.join(app.static_folder, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(audio_dir, filename)
    with open(audio_path, "wb") as f:
        f.write(tts_response.audio_content)

    return jsonify({
        "text": reply_text,
        "audio_url": f"/static/audio/{filename}"
    })

# ── エラーハンドリング ──

@app.errorhandler(404)
def page_not_found(e):
    return render_template("ja/404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("ja/500.html"), 500

# ── 起動設定 ──

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
