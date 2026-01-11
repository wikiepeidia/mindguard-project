document.addEventListener("DOMContentLoaded", function () {
  // --- Scammer Report Support Chat ---
  const btnToggleSupportChat = document.getElementById("btnToggleSupportChat");
  const supportChatModalEl = document.getElementById("supportChatModal");
  const btnSendSupportChat = document.getElementById("btnSendSupportChat");
  const supportChatInput = document.getElementById("supportChatInput");
  const supportChatBody = document.getElementById("supportChatBody");
  
  if (btnToggleSupportChat && supportChatModalEl) {
      let supportChatModal = new bootstrap.Modal(supportChatModalEl);
      btnToggleSupportChat.addEventListener("click", () => {
          supportChatModal.show();
      });
  }

  async function handleSendSupport() {
      if (!supportChatInput || !supportChatBody) return;
      
      const message = supportChatInput.value.trim();
      if (!message) return;

      // Add user message
      const userDiv = document.createElement("div");
      userDiv.className = "alert alert-primary mb-2";
      userDiv.innerHTML = `<strong>Bạn:</strong> ${message}`;
      supportChatBody.appendChild(userDiv);
      
      supportChatInput.value = '';
      supportChatBody.scrollTop = supportChatBody.scrollHeight;

      try {
          const response = await fetch('/chatbot/support', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({message: message})
          });
          const data = await response.json();
          
          // Add bot reply
          const botDiv = document.createElement("div");
          botDiv.className = "alert alert-success mb-2";
          botDiv.innerHTML = `<strong>Trợ lý:</strong> ${data.reply.replace(/\n/g, '<br>')}`;
          supportChatBody.appendChild(botDiv);
          
          supportChatBody.scrollTop = supportChatBody.scrollHeight;
      } catch (error) {
          console.error('Error:', error);
      }
  }

  if (btnSendSupportChat) {
      btnSendSupportChat.addEventListener("click", handleSendSupport);
  }

  if (supportChatInput) {
      supportChatInput.addEventListener("keypress", function(e) {
          if (e.key === "Enter") handleSendSupport();
      });
  }
});
