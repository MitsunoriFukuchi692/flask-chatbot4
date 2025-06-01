# app.py

from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)


# ────────── 日本語サイトのルーティング ───────────────────

@app.route("/")
@app.route("/ja/")
def index_jp():
    """
    日本語トップページ
    URL:
      - /
      - /ja/
    テンプレート: templates/ja/index.html
    """
    return render_template("ja/index.html")


@app.route("/ja/chatbot")
def chatbot_jp():
    """
    日本語チャットページ
    URL: /ja/chatbot
    テンプレート: templates/ja/chatbot.html
    """
    return render_template("ja/chatbot.html")


@app.route("/api/ja/chat", methods=["POST"])
def chat_api_jp():
    """
    日本語用チャットAPI（AJAX から呼び出す想定）
    URL: /api/ja/chat
    リクエスト: JSON { "message": "<ユーザーが入力したテキスト>" }
    レスポンス: JSON { "reply": "<ボットの返答テキスト>", "voice_url": "<音声ファイルのURL>" }
    """
    data = request.get_json()
    user_msg = data.get("message", "")

    # ── 実際はここに ChatGPT 呼び出しなどのロジックを実装してください ──
    # 例として、固定のダミー返答／ダミー音声URLを返しています。
    bot_reply = generate_bot_reply_jp(user_msg)
    voice_url = generate_tts_jp(bot_reply)  # 実際は Google TTS 等を呼び出して URL を生成

    return jsonify({
        "reply": bot_reply,
        "voice_url": voice_url
    })


def generate_bot_reply_jp(user_input: str) -> str:
    """
    日本語のボット返答を生成するサンプル関数。
    実際には OpenAI ChatGPT API などを呼び出してください。
    """
    # ここでは単純に入力を受けて文字列を返す例
    if not user_input:
        return "何か入力してください。"
    return f"（ダミー返答）あなたは「{user_input}」と入力しましたね。"


def generate_tts_jp(text: str) -> str:
    """
    日本語テキストを音声化して URL を返すサンプル関数。
    実際には Google Cloud Text-to-Speech などを呼び出し、
    生成された MP3/OGG ファイルを static 配下に保存して URL を返してください。
    """
    # ダミーとして static/audio/jp_dummy.mp3 を返す例
    return url_for("static", filename="audio/jp_dummy.mp3")


# ────────── 英語サイトのルーティング ───────────────────

@app.route("/en/")
def index_en():
    """
    英語トップページ
    URL: /en/
    テンプレート: templates/en/index.html
    """
    return render_template("en/index.html")


@app.route("/en/chatbot")
def chatbot_en():
    """
    英語チャットページ
    URL: /en/chatbot
    テンプレート: templates/en/chatbot.html
    """
    return render_template("en/chatbot.html")


@app.route("/api/en/chat", methods=["POST"])
def chat_api_en():
    """
    英語用チャットAPI（AJAX から呼び出す想定）
    URL: /api/en/chat
    リクエスト: JSON { "message": "<ユーザーが入力したテキスト>" }
    レスポンス: JSON { "reply": "<ボットの返答テキスト>", "voice_url": "<音声ファイルのURL>" }
    """
    data = request.get_json()
    user_msg = data.get("message", "")

    # ── 実際は ChatGPT や Google TTS を呼び出して英語返答を生成する実装を入れてください ──
    bot_reply = generate_bot_reply_en(user_msg)
    voice_url = generate_tts_en(bot_reply)

    return jsonify({
        "reply": bot_reply,
        "voice_url": voice_url
    })


def generate_bot_reply_en(user_input: str) -> str:
    """
    英語のボット返答を生成するサンプル関数。
    実際には OpenAI ChatGPT API などを呼び出してください。
    """
    if not user_input:
        return "Please type something."
    return f"(Dummy reply) You said: \"{user_input}\""


def generate_tts_en(text: str) -> str:
    """
    英語テキストを音声化して URL を返すサンプル関数。
    実際には Google Cloud Text-to-Speech などを呼び出し、
    生成された音声ファイルを static 配下に保存して URL を返してください。
    """
    # ダミーとして static/audio/en_dummy.mp3 を返す例
    return url_for("static", filename="audio/en_dummy.mp3")


# ────────── メイン実行部 ───────────────────

if __name__ == "__main__":
    # デバッグモードで起動。公開サーバーに上げる際は debug=False に変更してください。
    app.run(debug=True)
