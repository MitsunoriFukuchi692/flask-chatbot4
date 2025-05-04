import json
import requests

# Supabase情報（あなたの環境に合わせて変更してください）
SUPABASE_URL = "https://uvseetukwotbmyqdfcaj.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2VldHVrd290Ym15cWRmY2FqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ1OTg3MzQsImV4cCI6MjA2MDE3NDczNH0.Jow9WA376Mo4xDYuyHUhkBAslxKb9VaLoTo1hasSVNY"

# テーブル名
SUPABASE_TABLE = "chat_logs"

# 保存されたchat_logs.jsonを読み込む
with open("chat_logs.json", "r", encoding="utf-8") as f:
    for line in f:
        try:
            log = json.loads(line.strip())
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
                headers={
                    "apikey": SUPABASE_API_KEY,
                    "Authorization": f"Bearer {SUPABASE_API_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                },
                json=log
            )
            if response.status_code == 201:
                print("✅ 保存成功:", log)
            else:
                print("⚠️ 失敗:", response.status_code, response.text)
        except Exception as e:
            print("❌ エラー:", e)