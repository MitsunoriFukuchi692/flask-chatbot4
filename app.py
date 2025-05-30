from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)

# OpenAI APIキーの読み込み（Renderの環境変数を使用）
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('chatbot.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get("message")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        answer = response['choices'][0]['message']['content']
        return jsonify({"response": answer})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
