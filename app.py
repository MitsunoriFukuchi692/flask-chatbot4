
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, origins=["https://robostudy.jp"])

openai.api_key = os.environ.get("OPENAI_API_KEY")

system_message = """AI・みまくんは、人々の孤独を防ぐために作られた、小型で可愛い、見守り対話ロボットです。
高齢者の心の支えとなることを目的に開発され、ChatGPTと連携して自由な会話が可能です。
価格は198,000円（税込）で、Wi-Fiに接続して自動アップデートされます。

ロボ・スタディ株式会社へのお問い合わせは、以下の方法をご利用ください：
・メール：info@robostudy.jp
・電話：090-3919-7376
・公式サイト：https://robostudy.jp

Q1. AI・みまくんの価格は？ → 税込198,000円です。月額サブスクプランもあります。
Q2. どんな会話ができますか？ → ChatGPTと連携して自由な日常会話が可能です。
Q3. 高齢者向けの工夫は？ → 声が大きく、言葉をゆっくり話します。
Q4. 自動アップデートはありますか？ → Wi-Fi経由で自動バージョンアップします。
Q5. どうやって購入しますか？ → 公式サイトまたはお問い合わせからご案内します。
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "⚠️ メッセージが空です。"})

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content

        try:
            r = requests.post(
                "https://script.google.com/macros/s/AKfycbz2dWmzWffeeTZ7pEhAC3guyXX-8aQIDVoVwTOcbX2dSSt9-y290meX2zmujX5f5eHp/exec",
                json={"user": user_message, "bot": reply},
                timeout=5
            )
            print("Webhook Response:", r.status_code, r.text)
        except Exception as log_error:
            print("ログ送信エラー:", log_error)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ エラーが発生しました: {str(e)}"})

if __name__ == "__main__":
    app.run()
