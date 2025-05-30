from flask import Flask, Blueprint, render_template, request, jsonify
import os

app = Flask(__name__)

# 日本語版
ja_bp = Blueprint("ja", __name__,
                  url_prefix="",
                  template_folder="templates/ja")
@ja_bp.route("/")
def index_ja():
    return render_template("chatbot.html")

# 英語版
en_bp = Blueprint("en", __name__,
                  url_prefix="/en",
                  template_folder="templates/en")
@en_bp.route("/")
def index_en():
    return render_template("chatbot.html")

app.register_blueprint(ja_bp)
app.register_blueprint(en_bp)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    # …API呼び出し…
    return jsonify({"response": "（生成返答）"})

if __name__=="__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
