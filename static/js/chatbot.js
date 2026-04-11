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
    const res  = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ message: text, lang: "ja" })
    });
    const data = await res.json();

    chatLog.innerHTML += `<div class="bot">Mima-kun: ${data.text}</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;

    audioPlayer.src = data.audio_url;
    audioPlayer.style.display = "block";
    await audioPlayer.play();

  } catch(err) {
    console.error(err);
    chatLog.innerHTML += `<div class="bot">⚠️ エラーが発生しました</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;
  }
});
