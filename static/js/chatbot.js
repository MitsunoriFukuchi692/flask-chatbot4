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
    const res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
     body: JSON.stringify({ message: text, lang: "ja", company: "robostudy" })
    const data = await res.json();

    chatLog.innerHTML += `<div class="bot">Mima-kun: ${data.text}</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;

    audioPlayer.src = data.audio_url;
    audioPlayer.style.display = "block";
    
    // 自動再生を試み、ブロックされた場合はプレーヤーを表示して手動再生
    audioPlayer.play().catch(() => {
      console.log("自動再生がブロックされました。再生ボタンを押してください。");
    });

  } catch(err) {
    console.error(err);
    chatLog.innerHTML += `<div class="bot">⚠️ エラーが発生しました</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;
  }
});

// 音声入力機能
const micBtn = document.getElementById("mic-btn");

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = "ja-JP";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  micBtn.addEventListener("click", () => {
    recognition.start();
    micBtn.textContent = "🔴";  // 録音中は赤に変わる
  });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    micBtn.textContent = "🎤";  // 元に戻す
  };

  recognition.onerror = (event) => {
    console.error("音声認識エラー:", event.error);
    micBtn.textContent = "🎤";
  };

  recognition.onend = () => {
    micBtn.textContent = "🎤";
  };

} else {
  // 音声認識非対応ブラウザの場合はボタンを隠す
  micBtn.style.display = "none";
}
