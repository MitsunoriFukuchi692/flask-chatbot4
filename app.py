from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)

@app.route("/")
@app.route("/ja/")
@app.route("/ja")
def index_jp():
    return render_template("ja/index.html")

@app.route("/ja/chatbot")
@app.route("/ja/chatbot/")
def chatbot_jp():
    return render_template("ja/chatbot.html")

@app.route("/ja/about")
@app.route("/ja/about/")
def about_jp():
    return render_template("ja/about.html")

@app.route("/api/ja/chat", methods=["POST"])
def chat_api_jp():
    data = request.get_json()
    user_msg = data.get("message", "")
    return jsonify({"reply": f"（ダミー返答）「{user_msg}」を受け取りました。", "voice_url": ""})

@app.route("/en/")
@app.route("/en")
def index_en():
    return render_template("en/index.html")

@app.route("/en/chatbot")
@app.route("/en/chatbot/")
def chatbot_en():
    return render_template("en/chatbot.html")

@app.route("/en/about")
@app.route("/en/about/")
def about_en():
    return render_template("en/about.html")

@app.route("/api/en/chat", methods=["POST"])
def chat_api_en():
    data = request.get_json()
    user_msg = data.get("message", "")
    return jsonify({"reply": f"(Sample reply) You said: \"{user_msg}\"", "voice_url": ""})

if __name__ == "__main__":
    app.run(debug=True)
