const chatForm    = document.getElementById("chat-form");
const userInput   = document.getElementById("user-input");
const chatLog     = document.getElementById("chat-log");
const audioPlayer = document.getElementById("audio-player");

chatForm.addEventListener("submit", async e => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;
  userInput.value = "";
  chatLog.innerHTML += `<div class="user">You: ${text}</div>`;
  try {
    // チャット返答を取得
    const res  = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();

    // キー名を "reply" に修正
    chatLog.innerHTML += `<div class="bot">Mima-kun: ${data.reply}</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;

    // TTSに返答テキストを送って音声を取得
    const ttsRes = await fetch("/tts", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ text: data.reply, lang: "ja" })
    });
    const audioBlob = await ttsRes.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    audioPlayer.src = audioUrl;
    audioPlayer.style.display = "block";
    await audioPlayer.play();

  } catch(err) {
    console.error(err);
    chatLog.innerHTML += `<div class="bot">⚠️ エラーが発生しました</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;
  }
});
