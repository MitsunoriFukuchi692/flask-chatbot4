import os
import uuid
from flask import Flask, render_template, request, jsonify
import openai
from google.cloud import texttospeech

# ── 環境変数から API キーを取得 ──
#  - OpenAI の API キーをあらかじめ環境変数 OPENAI_API_KEY にセットしておきます。
#  - Google TTS は、アプリケーション側で GOOGLE_APPLICATION_CREDENTIALS 環境変数に
#    サービスアカウントの JSON キーのパスを渡しておくか、Workload Identity を利用する方法でも OK。
openai.api_key = os.getenv("OPENAI_API_KEY")

# ── Flask アプリ初期化 ──
app = Flask(
    __name__,
    static_folder="static",      # static/ 以下のファイルはそのまま配信される
    template_folder="templates"  # templates/ 以下の .html ファイルがテンプレート
)

# ──────────────────────────────────────────
#  1) 日本語版 ページルート定義
# ──────────────────────────────────────────

@app.route("/", methods=["GET"])
def home_ja():
    """
    日本語トップページ → templates/ja/index.html を返す
    URL: /
    """
    return render_template("ja/index.html")


@app.route("/about", methods=["GET"])
def about_ja():
    """
    日本語 About ページ → templates/ja/about.html を返す
    URL: /about
    """
    return render_template("ja/about.html")


@app.route("/products", methods=["GET"])
def products_ja():
    """
    日本語 Products（製品紹介） → templates/ja/products.html を返す
    URL: /products
    """
    return render_template("ja/products.html")


@app.route("/services", methods=["GET"])
def services_ja():
    """
    日本語 Services（サービス紹介） → templates/ja/services.html を返す
    URL: /services
    """
    return render_template("ja/services.html")


@app.route("/contact", methods=["GET"])
def contact_ja():
    """
    日本語 Contact（お問い合わせ） → templates/ja/contact.html を返す
    URL: /contact
    """
    return render_template("ja/contact.html")


@app.route("/chatbot", methods=["GET"])
@app.route("/chatbot/", methods=["GET"])
def chatbot_ja():
    """
    日本語チャットボット UI → templates/ja/chatbot.html を返す
    URL: /chatbot or /chatbot/
    """
    return render_template("ja/chatbot.html")


# もし他に日本語のページがあれば、同様に @app.route()→render_template("ja/○○.html") を追加します。


# ──────────────────────────────────────────
#  2) 英語版 ページルート定義
# ──────────────────────────────────────────

@app.route("/en", methods=["GET"])
@app.route("/en/", methods=["GET"])
def home_en():
    """
    英語トップページ → templates/en/index.html を返す
    URL: /en or /en/
    """
    return render_template("en/index.html")


@app.route("/en/about", methods=["GET"])
@app.route("/en/about/", methods=["GET"])
def about_en():
    """
    英語 About ページ → templates/en/about.html を返す
    URL: /en/about or /en/about/
    """
    return render_template("en/about.html")


@app.route("/en/products", methods=["GET"])
@app.route("/en/products/", methods=["GET"])
def products_en():
    """
    英語 Products ページ → templates/en/products.html を返す
    URL: /en/products or /en/products/
    """
    return render_template("en/products.html")


@app.route("/en/services", methods=["GET"])
@app.route("/en/services/", methods=["GET"])
def services_en():
    """
    英語 Services ページ → templates/en/services.html を返す
    URL: /en/services or /en/services/
    """
    return render_template("en/services.html")


@app.route("/en/contact", methods=["GET"])
@app.route("/en/contact/", methods=["GET"])
def contact_en():
    """
    英語 Contact ページ → templates/en/contact.html を返す
    URL: /en/contact or /en/contact/
    """
    return render_template("en/contact.html")


@app.route("/en/chatbot_en", methods=["GET"])
@app.route("/en/chatbot_en/", methods=["GET"])
def chatbot_en():
    """
    英語チャットボット UI → templates/en/chatbot.html を返す
    URL: /en/chatbot_en or /en/chatbot_en/
    """
    return render_template("en/chatbot.html")


# もし他に英語のページがあれば、同様に @app.route()→render_template("en/○○.html") を追加します。


# ──────────────────────────────────────────
#  3) チャットボット用 AJAX POST エンドポイント
# ──────────────────────────────────────────

@app.route("/chat", methods=["POST"])
def chat():
    """
    フロントエンド (chatbot.js) からの POST を受ける。
    リクエスト JSON:
      { "message": "...", "lang": "ja" もしくは "en" }
    """
    data = request.get_json()
    user_text = data.get("message", "")
    lang = data.get("lang", "ja")

    # ── 1) OpenAI ChatCompletion の呼び出し ──
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = completion.choices[0].message.content
    except Exception as e:
        # エラー時はブラウザ側にエラーメッセージを返す
        return jsonify({"text": f"Error generating response: {e}", "audio_url": ""}), 500

    # ── 2) Google TTS の呼び出し ──
    try:
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=reply_text)

        # 言語コードを lang パラメータで切り替え
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

    # ── 3) static/audio/ に MP3 を保存 ──
    audio_dir = os.path.join(app.static_folder, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(audio_dir, filename)
    with open(audio_path, "wb") as f:
        f.write(tts_response.audio_content)

    # ── 4) JSON でテキストと音声 URL を返却 ──
    return jsonify({
        "text": reply_text,
        "audio_url": f"/static/audio/{filename}"
    })


# ──────────────────────────────────────────
#  5) エラーハンドリング (任意)
# ──────────────────────────────────────────

@app.errorhandler(404)
def page_not_found(e):
    """
    404 エラーが発生したとき、テンプレート 404.html を返す例。
    （ templates/ja/404.html / templates/en/404.html を用意しておくとよい）
    """
    # Accept-Language ヘッダで切り替え、もしくは URL 先頭 "/en" の有無で判断しても良い
    return render_template("ja/404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    """
    500 エラーが発生したときに表示するテンプレート例。
    """
    return render_template("ja/500.html"), 500


# ──────────────────────────────────────────
#  6) アプリ起動設定
# ──────────────────────────────────────────

if __name__ == "__main__":
    # ローカルで開発するとき：
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
