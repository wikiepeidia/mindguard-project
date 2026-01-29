document.addEventListener("DOMContentLoaded", function () {
  const fab = document.getElementById("chatbotToggle");
  const panel = document.getElementById("chatbotPanel");
  const closeBtn = document.getElementById("chatbotClose");
  const form = document.getElementById("chatbotForm");
  const input = document.getElementById("chatbotInput");
  const messages = document.getElementById("chatbotMessages");

  if (!fab || !panel || !form) {
    return;
  }

  fab.addEventListener("click", () => {
    panel.style.display = panel.style.display === "flex" ? "none" : "flex";
  });

  closeBtn.addEventListener("click", () => {
    panel.style.display = "none";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    appendMessage(text, "user");
    input.value = "";
    try {
      const res = await fetch("/api/chatbot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      appendMessage(data.reply, "bot");
    } catch (err) {
      appendMessage("Có lỗi khi kết nối tới chatbot. Hãy thử lại sau.", "bot");
      console.error(err);
    }
  });

  function appendMessage(text, type) {
    const div = document.createElement("div");
    div.classList.add("chatbot-message", type);
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }
});
