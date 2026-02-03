document.getElementById('checkBtn').addEventListener('click', async () => {
    const query = document.getElementById('checkInput').value;
    const resultDiv = document.getElementById('result');
    
    if (!query) return;
    
    resultDiv.innerHTML = 'Đang kiểm tra...';
    
    // Replace with your actual MindGuard URL (e.g., localhost or production)
    const API_URL = 'http://127.0.0.1:5000/api/v1/check?q=' + encodeURIComponent(query);
    
    try {
        const response = await fetch(API_URL);
        const data = await response.json();
        
        if (data.found) {
            resultDiv.innerHTML = `
                <div class="danger">
                    <strong>⚠️ CẢNH BÁO CAO</strong><br>
                    Đối tượng: ${data.data.type}<br>
                    Báo cáo: ${data.data.reports_count} lượt
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="success">
                    <strong>✅ An toàn (Chưa có báo cáo)</strong><br>
                    Tuy nhiên hãy luôn cảnh giác.
                </div>
            `;
        }
    } catch (e) {
        resultDiv.textContent = 'Lỗi kết nối tới server MindGuard.';
    }
});
