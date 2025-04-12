from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = "sk-あなたのOpenAIキー"

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}]
    )
    return jsonify({"reply": response.choices[0].message['content']})

if __name__ == "__main__":
    app.run()
