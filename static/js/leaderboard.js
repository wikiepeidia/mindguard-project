document.addEventListener('DOMContentLoaded', function() {
    // Only attach if element exists
    const searchInput = document.getElementById('localSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            let input = this.value.toLowerCase();
            let rows = document.querySelectorAll('#blacklistTable tbody tr');
            
            rows.forEach(row => {
                let text = row.innerText.toLowerCase();
                row.style.display = text.includes(input) ? '' : 'none';
            });
        });
    }
});

function showDetail(element) {
    const identifier = element.getAttribute('data-identifier');
    const name = element.getAttribute('data-name');
    const type = element.getAttribute('data-type');
    const platform = element.getAttribute('data-platform');
    const desc = element.getAttribute('data-desc');
    const reports = element.getAttribute('data-reports');
    const date = element.getAttribute('data-date');
    let imageRaw = element.getAttribute('data-image');

    document.getElementById('detailId').innerText = identifier;
    document.getElementById('detailName').innerText = name && name !== 'None' ? name : 'Chưa rõ danh tính';
    document.getElementById('detailType').innerText = type;
    document.getElementById('detailPlatform').innerText = platform || 'Không rõ';
    document.getElementById('detailReports').innerText = reports + ' lượt';
    document.getElementById('detailDate').innerText = date;
    document.getElementById('detailDesc').innerText = desc;

    const evidenceSec = document.getElementById('evidenceSection');
    const noEvidenceSec = document.getElementById('noEvidenceSection');
    const evidenceImg = document.getElementById('detailImage');
    
    let imageUrl = '';
    if (imageRaw && imageRaw !== 'None') {
        try {
            const images = JSON.parse(imageRaw);
            if (Array.isArray(images) && images.length > 0) {
                imageUrl = images[0];
            }
        } catch (e) {
            imageUrl = imageRaw;
        }
    }

    if (imageUrl && imageUrl.length > 5) {
        evidenceImg.src = imageUrl;
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
