// script.js — handles UI rendering, sends messages to /chat
const chatEl = document.getElementById("chat");
const optionsEl = document.getElementById("options");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("send");

// helper to create message bubble
function addMessage(text, who = "bot") {
  const div = document.createElement("div");
  div.className = "msg " + (who === "user" ? "user" : "bot");
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

// render options as three buttons
function renderOptions(options) {
  optionsEl.innerHTML = "";
  if (!options || !options.length) return;
  options.forEach(opt => {
    const btn = document.createElement("button");
    btn.className = "opt-btn";
    btn.textContent = opt.text;
    btn.onclick = () => {
      // when user clicks an option, send it as message
      sendMessage(opt.text);
    };
    optionsEl.appendChild(btn);
  });
}

// call server /chat with message
async function sendMessage(text) {
  if (!text || !text.trim()) return;
  // show user bubble
  addMessage(text, "user");
  inputEl.value = "";
  // show typing indicator
  const typing = document.createElement("div");
  typing.className = "msg bot";
  typing.textContent = "Typing…";
  chatEl.appendChild(typing);
  chatEl.scrollTop = chatEl.scrollHeight;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text})
    });
    const payload = await res.json();
    typing.remove();
    if (!payload.ok) {
      addMessage("Sorry, an error occurred.", "bot");
      renderOptions([]);
      return;
    }
    // show bot reply
    addMessage(payload.reply, "bot");
    // render three options
    renderOptions(payload.options || []);
  } catch (err) {
    typing.remove();
    addMessage("Network error. Please try again.", "bot");
  }
}

// on send button click or Enter
sendBtn.addEventListener("click", () => sendMessage(inputEl.value));
inputEl.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage(inputEl.value);
});

// initial load: fetch the start node by sending a harmless message like "start"
window.addEventListener("load", () => {
  // request start node by sending "start"
  sendMessage("start");
});
