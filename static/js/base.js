document.addEventListener('DOMContentLoaded', function () {
    try {
        AOS.init({ duration: 800, once: true });
    } catch (e) {
        // AOS library may fail to load from CDN — do not crash the rest of the handler.
    }

    // --- JS CHO HIỆU ỨNG HẠT NỀN (Áo mới) ---
    const canvas = document.getElementById('network-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let particles = [];

        function initCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            particles = [];
            for (let i = 0; i < 80; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: (Math.random() - 0.5) * 0.5,
                    vy: (Math.random() - 0.5) * 0.5
                });
            }
        }

        function animateCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0ea5e9';
            ctx.strokeStyle = 'rgba(14, 165, 233, 0.34)';
            particles.forEach((p, i) => {
                p.x += p.vx; p.y += p.vy;
                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
                ctx.beginPath(); ctx.arc(p.x, p.y, 2.2, 0, Math.PI * 2); ctx.fill();
                for (let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    let dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                    if (dist < 150) {
                        ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
                    }
                }
            });
            requestAnimationFrame(animateCanvas);
        }

        initCanvas();
        animateCanvas();
        window.onresize = initCanvas;
    }

    // Auto-hide flash alerts after a short delay for cleaner UX.
    // Error (danger) alerts are excluded — users need time to read them.
    document.querySelectorAll('.alert.alert-dismissible').forEach(function (alertElement) {
        // Skip auto-dismiss for error/danger alerts — they require user acknowledgment.
        var isError = alertElement.classList.contains('alert-danger') ||
            alertElement.classList.contains('alert-error');
        if (isError) return;

        var timer = null;

        var dismiss = function () {
            // Add the fade-out class for a smooth CSS transition.
            alertElement.classList.add('alert-auto-dismiss');
            // After the CSS transition completes (500ms), remove the element from the DOM.
            alertElement.addEventListener('transitionend', function handler() {
                alertElement.removeEventListener('transitionend', handler);
                alertElement.remove();
            });
            // Fallback removal in case transitionend does not fire (e.g., display:none ancestor).
            setTimeout(function () {
                if (alertElement.parentNode) {
                    alertElement.remove();
                }
            }, 600);
        };

        var startTimer = function () {
            timer = setTimeout(dismiss, 2000);
        };

        startTimer();

        // Pause the timer while the user hovers over the alert.
        alertElement.addEventListener('mouseenter', function () { clearTimeout(timer); });
        alertElement.addEventListener('mouseleave', startTimer);
    });

    // --- CHATBOT LOGIC (Giữ nguyên 100% của bạn) ---
    const chatInput = document.getElementById("chatInput");
    const sendChatBtn = document.getElementById("sendChatBtn");
    const chatbox = document.getElementById("chatbox");

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("div");
        chatLi.classList.add("chat-msg", className);
        chatLi.innerHTML = message;
        return chatLi;
    }

    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        chatbox.appendChild(createChatLi(userMessage, "msg-outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
        chatInput.value = "";

        const loadingLi = createChatLi('<i class="fas fa-ellipsis-h fa-bounce"></i> Đang phân tích...', "msg-incoming");
        chatbox.appendChild(loadingLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);

        // Use the global variable for URL
        const apiUrl = window.CHATBOT_API_URL || "/chatbot/api"; // Fallback path if variable missing

        fetch(apiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage })
        }).then(res => res.json()).then(data => {
            chatbox.removeChild(loadingLi);
            chatbox.appendChild(createChatLi(data.reply, "msg-incoming"));
            chatbox.scrollTo(0, chatbox.scrollHeight);
        }).catch(() => {
            chatbox.removeChild(loadingLi);
            chatbox.appendChild(createChatLi("❌ Lỗi kết nối AI. Vui lòng thử lại.", "msg-incoming"));
        });
    }

    if (sendChatBtn) {
        sendChatBtn.addEventListener("click", handleChat);
        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleChat();
            }
        });
    }
});
