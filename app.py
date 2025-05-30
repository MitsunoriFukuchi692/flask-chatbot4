import os
from flask import Flask, render_template, request, jsonify

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"  # デフォルトですが、念のため明示します
)

# ---- 日本語トップページ ----
@app.route("/")
def index_ja():
    # サブフォルダ付きでテンプレートを指定
    return render_template("ja/chatbot.html")

# ---- 英語トップページ ----
@app.route("/en/")
def index_en():
    return render_template("en/chatbot.html")

# ---- チャット用APIエンドポイント ----
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    message = data.get("message")
    # … ここに OpenAI API コール等のロジック …
    response_text = "（生成された返答）"
    return jsonify({"response": response_text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
