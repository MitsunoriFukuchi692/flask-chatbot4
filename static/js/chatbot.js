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
    // エンドポイントを /chat に変更
    const res  = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();

    // レスポンス内の JSON キー名に合わせて表示
    chatLog.innerHTML += `<div class="bot">Mima-kun: ${data.text}</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;

    // audio_url を直接使う
    audioPlayer.src = data.audio_url;
    audioPlayer.style.display = "block";
    await audioPlayer.play();
  } catch(err) {
    console.error(err);
    chatLog.innerHTML += `<div class="bot">⚠️ エラーが発生しました</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;
  }
});
