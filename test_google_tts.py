from google.cloud import texttospeech
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-credentials.json"

# 環境変数が設定されているか確認（念のため）
print("GOOGLE_APPLICATION_CREDENTIALS =", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

# クライアント初期化
client = texttospeech.TextToSpeechClient()

# 合成する音声のリクエスト
synthesis_input = texttospeech.SynthesisInput(text="こんにちは、テストです")

voice = texttospeech.VoiceSelectionParams(
    language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

# 音声生成
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# 保存
with open("test_output.mp3", "wb") as out:
    out.write(response.audio_content)

print("✅ 音声ファイル 'test_output.mp3' を保存しました。")
