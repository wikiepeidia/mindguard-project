function filterLive(button, filterType) {
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');

    const items = document.querySelectorAll('.scammer-item');
    items.forEach(item => {
        let show = true;

        if (filterType === 'high-risk') {
            show = item.dataset.riskLevel === 'high';
        } else if (filterType === 'verified') {
            show = item.dataset.verification === 'verified';
        } else if (filterType === 'bank') {
            show = item.dataset.reportType === 'bank';
        } else if (filterType === 'website') {
            show = item.dataset.reportType === 'website';
        } else if (filterType === 'general') {
            show = item.dataset.reportType === 'general';
        }
        // 'all' shows everything

        item.style.display = show ? 'block' : 'none';
    });
}

function showDetail(element) {
    const identifier = element.getAttribute('data-identifier');
    const name = element.getAttribute('data-name');
    const type = element.getAttribute('data-type');
    const platform = element.getAttribute('data-platform');
    const desc = element.getAttribute('data-desc');
    const reports = element.getAttribute('data-reports');
    const confirmed = element.getAttribute('data-confirmed') || '0';
    const riskScore = element.getAttribute('data-risk-score') || '0';
    const verificationStatus = element.getAttribute('data-verification-status') || 'unverified';
    const date = element.getAttribute('data-date');
    const image = element.getAttribute('data-image');

    document.getElementById('detailId').innerText = identifier;
    document.getElementById('detailName').innerText = name;
    document.getElementById('detailType').innerText = type;
    document.getElementById('detailPlatform').innerText = platform || 'Không rõ';
    document.getElementById('detailReports').innerText = reports + ' lượt';
    document.getElementById('detailDate').innerText = date;
    document.getElementById('detailDesc').innerText = desc;

    const evidenceSec = document.getElementById('evidenceSection');
    const noEvidenceSec = document.getElementById('noEvidenceSection');
    const evidenceImg = document.getElementById('detailImage');

    if (image && image !== 'None' && image !== '' && image !== '[]') {
        evidenceImg.src = image;
        evidenceSec.classList.remove('d-none');
        evidenceSec.classList.add('d-flex');
        noEvidenceSec.classList.add('d-none');
        noEvidenceSec.classList.remove('d-flex');
    } else {
        evidenceSec.classList.add('d-none');
        evidenceSec.classList.remove('d-flex');
        noEvidenceSec.classList.remove('d-none');
        noEvidenceSec.classList.add('d-flex');
    }

    new bootstrap.Modal(document.getElementById('scammerDetailModal')).show();
}

function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) { alert("Vui lòng nhập thông tin!"); return; }
    const modal = new bootstrap.Modal(document.getElementById('searchResultModal'));
    document.getElementById('resultIcon').className = 'fas fa-circle-notch fa-spin text-info';
    document.getElementById('resultTitle').innerText = 'Đang quét...';
    document.getElementById('foundList').classList.add('d-none');
    modal.show();

    // Use a relative path or global variable for the URL if needed, 
    // but in Flask templates usually renders this. 
    // Since we moved to JS file, we'll need to pass the URL or rely on it being constant.
    // For now assuming the path is /search_scammer or we pass it via data attribute in HB later.
    // Ideally we should keep the URL generation in template or pass it to a init function.
    // Let's assume '/search_scammer' for now, or use a variable SEARCH_URL if defined.
    const searchUrl = window.SEARCH_URL || '/search_scammer'; 

    fetch(searchUrl, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: query })
    }).then(res => res.json()).then(data => {
        if (data.status === 'danger') {
            document.getElementById('resultIcon').className = 'fas fa-exclamation-triangle text-danger';
            document.getElementById('resultTitle').innerText = 'CẢNH BÁO!';
            document.getElementById('resultDesc').innerHTML = `Thông tin <b>"${query}"</b> bị báo cáo <b>${data.total_reports} lần</b>.`;
            let html = '';
            data.data.forEach(item => {
                html += `<div class="d-flex align-items-center mb-2 border-bottom border-white border-opacity-5 pb-2"><i class="fas fa-user-secret text-danger me-3"></i><div><div class="text-white fw-bold">${item.identifier}</div><div class="small text-slate-500">${item.type}</div></div></div>`;
            });
            document.getElementById('foundList').innerHTML = html;
            document.getElementById('foundList').classList.remove('d-none');
        } else {
            document.getElementById('resultIcon').className = 'fas fa-shield-alt text-success';
            document.getElementById('resultTitle').innerText = 'CHƯA CÓ DỮ LIỆU';
            document.getElementById('resultDesc').innerText = `Hệ thống chưa ghi nhận báo cáo về "${query}".`;
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if(searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') performSearch();
        });
    }
});
