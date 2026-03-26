document.addEventListener('DOMContentLoaded', function () {
    const app = document.getElementById('chatbotApp');
    const chatContainer = document.getElementById('chatHistoryContainer');
    const messageList = document.getElementById('chatMessageList');
    const emptyState = document.getElementById('chatEmptyState');
    const sessionList = document.getElementById('chatSessionList');
    const emptySidebar = document.getElementById('chatEmptySidebar');
    const composerForm = document.getElementById('chatbotComposerForm');
    const messageInput = document.getElementById('chatbot-message');
    const sessionIdInput = document.getElementById('chatbotSessionId');
    const panelTitle = document.getElementById('chatbotPanelTitle');
    const panelCopy = document.getElementById('chatbotPanelCopy');
    const sessionCount = document.getElementById('chatSessionCount');
    const statusValue = document.getElementById('chatStatusValue');
    const suggestionForms = document.querySelectorAll('.chatbot-suggestion-form');

    if (!app || !chatContainer || !composerForm || !messageInput) {
        return;
    }

    let currentSessionId = (sessionIdInput && sessionIdInput.value) || app.dataset.currentSessionId || '';
    let isSending = false;

    function escapeHtml(text) {
        return String(text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function renderTextWithBreaks(text) {
        return escapeHtml(text).replace(/\n/g, '<br>');
    }

    function isNearBottom() {
        const remainingDistance = chatContainer.scrollHeight - chatContainer.clientHeight - chatContainer.scrollTop;
        return remainingDistance < 120;
    }

    function scrollToBottom(force) {
        if (force || isNearBottom()) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    function createMessageRow(sender, text) {
        const isUser = sender === 'user';
        const row = document.createElement('div');
        row.className = 'chatbot-message-row ' + (isUser ? 'is-user' : 'is-bot');

        if (!isUser) {
            const botAvatar = document.createElement('div');
            botAvatar.className = 'chatbot-avatar';
            botAvatar.innerHTML = '<i class="fas fa-robot"></i>';
            row.appendChild(botAvatar);
        }

        const stack = document.createElement('div');
        stack.className = 'chatbot-message-stack ' + (isUser ? 'align-end' : '');

        const bubble = document.createElement('div');
        bubble.className = 'chatbot-bubble ' + (isUser ? 'chatbot-bubble-user' : 'chatbot-bubble-bot');
        bubble.innerHTML = renderTextWithBreaks(text);
        stack.appendChild(bubble);

        const meta = document.createElement('small');
        meta.className = 'chatbot-message-meta';
        meta.textContent = isUser ? 'Bạn' : 'MindGuard Bot';
        stack.appendChild(meta);
        row.appendChild(stack);

        if (isUser) {
            const userAvatar = document.createElement('div');
            userAvatar.className = 'chatbot-avatar chatbot-avatar-user';
            userAvatar.innerHTML = '<i class="fas fa-user"></i>';
            row.appendChild(userAvatar);
        }

        return row;
    }

    function ensureMessageListVisible() {
        messageList.classList.remove('d-none');
        emptyState.classList.add('d-none');
    }

    function appendMessage(sender, text) {
        ensureMessageListVisible();
        messageList.appendChild(createMessageRow(sender, text));
    }

    function updateSessionCount() {
        if (!sessionCount || !sessionList) {
            return;
        }

        sessionCount.textContent = String(sessionList.querySelectorAll('.chatbot-session-item').length);
    }

    function setActiveSession(sessionId) {
        if (!sessionList) {
            return;
        }

        sessionList.querySelectorAll('.chatbot-session-item').forEach(function (item) {
            item.classList.toggle('active', item.dataset.sessionId === String(sessionId));
        });
    }

    function buildSessionItem(sessionData) {
        const item = document.createElement('a');
        item.href = sessionData.url;
        item.className = 'chatbot-session-item active';
        item.dataset.sessionId = String(sessionData.id);
        item.innerHTML = '' +
            '<div class="chatbot-session-icon"><i class="fas fa-message"></i></div>' +
            '<div class="chatbot-session-content">' +
            '<span class="chatbot-session-title"></span>' +
            '<span class="chatbot-session-time"></span>' +
            '</div>';

        item.querySelector('.chatbot-session-title').textContent = sessionData.title || 'Cuộc trò chuyện';
        item.querySelector('.chatbot-session-time').textContent = sessionData.updated_at || 'Không rõ thời gian';
        return item;
    }

    function upsertSessionItem(sessionData) {
        if (!sessionList || !emptySidebar) {
            return;
        }

        let item = sessionList.querySelector('[data-session-id="' + String(sessionData.id) + '"]');
        if (!item) {
            item = buildSessionItem(sessionData);
        } else {
            item.href = sessionData.url;
            item.querySelector('.chatbot-session-title').textContent = sessionData.title || 'Cuộc trò chuyện';
            item.querySelector('.chatbot-session-time').textContent = sessionData.updated_at || 'Không rõ thời gian';
        }

        item.classList.add('active');
        sessionList.classList.remove('d-none');
        emptySidebar.classList.add('d-none');
        sessionList.prepend(item);
        setActiveSession(sessionData.id);
        updateSessionCount();
    }

    function updateConversationState(sessionData) {
        currentSessionId = String(sessionData.id);

        if (sessionIdInput) {
            sessionIdInput.value = currentSessionId;
        }

        app.dataset.currentSessionId = currentSessionId;

        if (panelTitle) {
            panelTitle.textContent = sessionData.title || 'Cuộc trò chuyện';
        }

        if (panelCopy) {
            panelCopy.textContent = 'Cuộc trò chuyện đang được lưu tự động vào lịch sử của bạn.';
        }

        if (statusValue) {
            statusValue.textContent = 'Đang xem lịch sử';
        }

        upsertSessionItem(sessionData);

        if (window.history && typeof window.history.replaceState === 'function') {
            window.history.replaceState({ sessionId: currentSessionId }, '', sessionData.url);
        }
    }

    function setSendingState(sending) {
        isSending = sending;
        messageInput.disabled = sending;
        composerForm.querySelectorAll('button').forEach(function (button) {
            button.disabled = sending;
        });
        suggestionForms.forEach(function (form) {
            form.querySelectorAll('button').forEach(function (button) {
                button.disabled = sending;
            });
        });
    }

    function sendMessage(message) {
        const trimmedMessage = String(message || '').trim();
        if (!trimmedMessage || isSending) {
            return;
        }

        const shouldStickToBottom = isNearBottom() || !currentSessionId;
        appendMessage('user', trimmedMessage);
        scrollToBottom(shouldStickToBottom);
        setSendingState(true);
        messageInput.value = '';

        fetch(app.dataset.sendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                message: trimmedMessage,
                session_id: currentSessionId || null
            })
        })
            .then(function (response) {
                return response.json().then(function (payload) {
                    return {
                        ok: response.ok,
                        payload: payload
                    };
                });
            })
            .then(function (result) {
                if (!result.ok) {
                    throw new Error(result.payload.error || 'Gửi tin nhắn thất bại.');
                }

                if (result.payload.session) {
                    updateConversationState(result.payload.session);
                }

                appendMessage('bot', result.payload.reply || 'MindGuard hiện chưa thể phản hồi.');
                scrollToBottom(true);
            })
            .catch(function (error) {
                appendMessage('bot', error.message || 'Đã xảy ra lỗi khi gửi tin nhắn. Vui lòng thử lại.');
                scrollToBottom(true);
            })
            .finally(function () {
                setSendingState(false);
                messageInput.focus();
            });
    }

    composerForm.addEventListener('submit', function (event) {
        event.preventDefault();
        sendMessage(messageInput.value);
    });

    suggestionForms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const submitter = event.submitter || form.querySelector('button[name="message"]');
            if (!submitter) {
                return;
            }

            sendMessage(submitter.value || submitter.getAttribute('value') || '');
        });
    });

    if (chatContainer.dataset.initialScroll === 'true') {
        requestAnimationFrame(function () {
            scrollToBottom(true);
        });
    }
});
