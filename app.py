# app.py

from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)


# ────────── 日本語サイトのルーティング ───────────────────

# 「/」と「/ja/」の両方で日本語トップページを返す
@app.route("/")
@app.route("/ja/")
@app.route("/ja")
def index_jp():
    """
    日本語トップページ
    URL: /      または /ja/  (末尾スラッシュの有無を両方カバー)
    テンプレート: templates/ja/index.html
    """
    return render_template("ja/index.html")


# 日本語チャットページ
@app.route("/ja/chatbot")
@app.route("/ja/chatbot/")
def chatbot_jp():
    """
    日本語チャットページ
    URL: /ja/chatbot  または /ja/chatbot/
    テンプレート: templates/ja/chatbot.html
    """
    return render_template("ja/chatbot.html")


# 日本語Aboutページ
@app.route("/ja/about")
@app.route("/ja/about/")
def about_jp():
    """
    日本語 About ページ
    URL: /ja/about  または /ja/about/
    テンプレート: templates/ja/about.html
    """
    return render_template("ja/about.html")


# 日本語チャットAPI
@app.route("/api/ja/chat", methods=["POST"])
def chat_api_jp():
    """
    日本語用チャットAPI（AJAX から呼び出す想定）
    URL: /api/ja/chat
    リクエスト: JSON { "message": "<ユーザーが入力>" }
    レスポンス: JSON { "reply": "<ボット応答>", "voice_url": "<音声ファイルURL>" }
    """
    data = request.get_json()
    user_msg = data.get("message", "")

    # ここに ChatGPT 呼び出しなどのロジックを入れてください
    bot_reply = generate_bot_reply_jp(user_msg)
    voice_url = generate_tts_jp(bot_reply)

    return jsonify({
        "reply": bot_reply,
        "voice_url": voice_url
    })


def generate_bot_reply_jp(user_input: str) -> str:
    """
    日本語返答のダミー実装例。実際は OpenAI ChatGPT API を呼び出してください。
    """
    if not user_input:
        return "何か入力してください。"
    return f"（サンプル返答）「{user_input}」を受け取りました。"


def generate_tts_jp(text: str) -> str:
    """
    日本語テキストを音声化し、その URL を返すダミー実装例。
    実運用では Google TTS などを使い、生成ファイルを static/audio/ に保存し URL を返してください。
    """
    # 例として static/audio/jp_dummy.mp3 が存在しているものとします
    return url_for("static", filename="audio/jp_dummy.mp3")


# ────────── 英語サイトのルーティング ───────────────────

# 「/en/」と「/en」の両方で英語トップページを返す
@app.route("/en/")
@app.route("/en")
def index_en():
    """
    英語トップページ
    URL: /en/  または /en
    テンプレート: templates/en/index.html
    """
    return render_template("en/index.html")


# 英語チャットページ（末尾あり／なしを両対応）
@app.route("/en/chatbot")
@app.route("/en/chatbot/")
def chatbot_en():
    """
    英語チャットページ
    URL: /en/chatbot  または /en/chatbot/
    テンプレート: templates/en/chatbot.html
    """
    return render_template("en/chatbot.html")


# 英語 About ページ（末尾あり／なしを両対応）
@app.route("/en/about")
@app.route("/en/about/")
def about_en():
    """
    英語 About ページ
    URL: /en/about  または /en/about/
    テンプレート: templates/en/about.html
    """
    return render_template("en/about.html")


# 英語チャットAPI
@app.route("/api/en/chat", methods=["POST"])
def chat_api_en():
    """
    英語用チャットAPI（AJAX から呼び出す想定）
    URL: /api/en/chat
    リクエスト: JSON { "message": "<ユーザーが入力>" }
    レスポンス: JSON { "reply": "<ボット応答>", "voice_url": "<音声ファイルURL>" }
    """
    data = request.get_json()
    user_msg = data.get("message", "")

    # ここに ChatGPT 呼び出しなどのロジックを入れてください
    bot_reply = generate_bot_reply_en(user_msg)
    voice_url = generate_tts_en(bot_reply)

    return jsonify({
        "reply": bot_reply,
        "voice_url": voice_url
    })


def generate_bot_reply_en(user_input: str) -> str:
    """
    英語返答のダミー実装例。実際は OpenAI ChatGPT API を呼び出してください。
    """
    if not user_input:
        return "Please type something."
    return f"(Sample reply) You said: \"{user_input}\""


def generate_tts_en(text: str) -> str:
    """
    英語テキストを音声化し、その URL を返すダミー実装例。
    実運用では Google TTS などを使い、生成ファイルを static/audio/ に保存し URL を返してください。
    """
    # 例として static/audio/en_dummy.mp3 が存在しているものとします
    return url_for("static", filename="audio/en_dummy.mp3")


# ────────── アプリケーション起動 ───────────────────

if __name__ == "__main__":
    # デバッグモードで起動。公開環境では debug=False に変更してください。
    app.run(debug=True)
