document.addEventListener('DOMContentLoaded', function () {
    AOS.init({ duration: 800, once: true });

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
    document.querySelectorAll('.alert.alert-dismissible').forEach((alertElement) => {
        const DISMISS_DELAY = 4000;
        let timer = null;

        function scheduleClose() {
            timer = setTimeout(() => {
                if (window.bootstrap && window.bootstrap.Alert) {
                    window.bootstrap.Alert.getOrCreateInstance(alertElement).close();
                } else {
                    alertElement.classList.remove('show');
                    alertElement.remove();
                }
            }, DISMISS_DELAY);
        }

        scheduleClose();

        alertElement.addEventListener('mouseenter', () => { if (timer) clearTimeout(timer); });
        alertElement.addEventListener('mouseleave', () => { scheduleClose(); });
    });

    // --- CHATBOT WIDGET LOGIC ---
    const chatInput = document.getElementById("chatInput");
    const sendChatBtn = document.getElementById("sendChatBtn");
    const chatbox = document.getElementById("chatbox");

    const STORAGE_KEY = "mindguard_widget_history";
    const MAX_HISTORY = 30; // tối đa 30 tin nhắn lưu lại

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("div");
        chatLi.classList.add("chat-msg", className);
        chatLi.innerHTML = message;
        return chatLi;
    };

    // Lưu 1 tin nhắn vào localStorage
    const saveMessage = (text, role) => {
        try {
            const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
            history.push({ text, role, ts: Date.now() });
            if (history.length > MAX_HISTORY) history.splice(0, history.length - MAX_HISTORY);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
        } catch (e) { /* localStorage không khả dụng */ }
    };

    // Khôi phục lịch sử khi mở trang
    const loadHistory = () => {
        try {
            const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
            if (history.length === 0) return;
            history.forEach(({ text, role }) => {
                const cls = role === "user" ? "msg-outgoing" : "msg-incoming";
                chatbox.appendChild(createChatLi(text, cls));
            });
            chatbox.scrollTo(0, chatbox.scrollHeight);
        } catch (e) { /* bỏ qua */ }
    };

    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        chatbox.appendChild(createChatLi(userMessage, "msg-outgoing"));
        saveMessage(userMessage, "user");
        chatbox.scrollTo(0, chatbox.scrollHeight);
        chatInput.value = "";

        const loadingLi = createChatLi('<i class="fas fa-ellipsis-h fa-bounce"></i> Đang phân tích...', "msg-incoming");
        chatbox.appendChild(loadingLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);

        const apiUrl = window.CHATBOT_API_URL || "/chatbot/api";

        fetch(apiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage })
        }).then(res => res.json()).then(data => {
            chatbox.removeChild(loadingLi);
            const reply = data.reply || "Xin lỗi, tôi chưa hiểu câu hỏi này.";
            chatbox.appendChild(createChatLi(reply, "msg-incoming"));
            saveMessage(reply, "bot");
            chatbox.scrollTo(0, chatbox.scrollHeight);
        }).catch(() => {
            chatbox.removeChild(loadingLi);
            const errMsg = "❌ Lỗi kết nối AI. Vui lòng thử lại.";
            chatbox.appendChild(createChatLi(errMsg, "msg-incoming"));
            saveMessage(errMsg, "bot");
        });
    };

    if (sendChatBtn) {
        loadHistory(); // khôi phục lịch sử khi load trang
        sendChatBtn.addEventListener("click", handleChat);
        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleChat();
            }
        });
    }

    const clearChatBtn = document.getElementById("clearChatBtn");
    if (clearChatBtn) {
        clearChatBtn.addEventListener("click", () => {
            try { localStorage.removeItem(STORAGE_KEY); } catch (e) { /* bỏ qua */ }
            // Giữ lại tin chào, xoá các tin khác
            const msgs = chatbox.querySelectorAll(".chat-msg:not(#welcomeMsg)");
            msgs.forEach(m => m.remove());
        });
    }
});
