import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "こんにちは！"}]
    )
    print("✅ 成功！応答内容:")
    print(response.choices[0].message.content)
except Exception as e:
    print("❌ エラーが発生しました:", e)
