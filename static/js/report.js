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

  // --- File Upload Validation (Security Check) ---
  const MAX_FILES = 10;
  
  function validateFileHeader(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = function(e) {
        if (e.target.readyState === FileReader.DONE) {
          const arr = (new Uint8Array(e.target.result)).subarray(0, 4);
          let header = "";
          for(let i = 0; i < arr.length; i++) {
            header += arr[i].toString(16).padStart(2, "0");
          }
          
          // Check magic numbers
          // PNG: 89504e47
          // JPG: ffd8...
          // GIF: 47494638 (GIF8)
          let isValid = false;
          if (header === "89504e47") isValid = true; 
          else if (header.startsWith("ffd8")) isValid = true;
          else if (header.startsWith("474946")) isValid = true;

          resolve({isValid, filename: file.name, header});
        }
      };
      reader.readAsArrayBuffer(file);
    });
  }

  function setupFileValidation(inputId) {
    const fileInput = document.getElementById(inputId);
    if (!fileInput) return;

    fileInput.addEventListener('change', async function(event) {
      const files = event.target.files;
      
      // 1. Check count
      if (files.length > MAX_FILES) {
        alert(`Bạn chỉ được chọn tối đa ${MAX_FILES} ảnh.`);
        this.value = ''; 
        return;
      }

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // 2. Check MIME type (Extension)
        if (!file.type.startsWith('image/')) {
            alert(`File "${file.name}" không phải là ảnh hợp lệ.`);
            this.value = '';
            return;
        }

        // 3. Deep Scan (Magic Cookies/Headers)
        try {
            const result = await validateFileHeader(file);
            if (!result.isValid) {
                console.warn(`Blocked spoofed file: ${result.filename} (Header: ${result.header})`);
                alert(`PHÁT HIỆN GIẢ MẠO!\nFile "${file.name}" có định dạng không hợp lệ.\nVui lòng chỉ tải lên file ảnh gốc (JPG, PNG, GIF).`);
                this.value = ''; // Block immediately
                return;
            }
        } catch (err) {
            console.error("Validation error:", err);
        }
      }
    });
  }

  setupFileValidation('bankEvidenceFile');
  setupFileValidation('webEvidenceFile');
});
