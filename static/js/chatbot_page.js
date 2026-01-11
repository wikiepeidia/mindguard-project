// Auto-scroll to bottom of chat history
document.addEventListener('DOMContentLoaded', function() {
    var chatContainer = document.getElementById("chatHistoryContainer");
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
