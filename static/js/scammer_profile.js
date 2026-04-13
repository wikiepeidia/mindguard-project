let isMasked = true;

function toggleMask() {
    const display = document.getElementById('identifierDisplay');
    const button = document.getElementById('maskToggle');
    // Ensure SCAMMER_DATA exists
    if (!window.SCAMMER_DATA) return;

    // Check login status
    if (!window.SCAMMER_DATA.isLoggedIn) {
        if (confirm('Để xem đầy đủ thông tin, bạn cần đăng nhập. Đi tới trang đăng nhập?')) {
            window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        }
        return;
    }

    if (isMasked) {
        display.textContent = window.SCAMMER_DATA.originalIdentifier;
        button.innerHTML = '<i class="fas fa-eye-slash"></i> Ẩn';
        isMasked = false;
    } else {
        display.textContent = window.SCAMMER_DATA.maskedIdentifier;
        button.innerHTML = '<i class="fas fa-eye"></i> Xem đầy đủ';
        isMasked = true;
    }
}

function showImageModal(src) {
    document.getElementById('modalImage').src = src;
    new bootstrap.Modal(document.getElementById('imageModal')).show();
}

function confirmReport() {
    // TODO: Implement confirm functionality
    alert('Chức năng xác nhận đang được phát triển!');
}

function shareWarning() {
    const url = window.location.href;
    // Prefer original identifier if logged in for better context, else just generic text
    let identifier = "đối tượng này";
    if (window.SCAMMER_DATA && window.SCAMMER_DATA.maskedIdentifier) {
        identifier = window.SCAMMER_DATA.maskedIdentifier;
    }

    if (navigator.share) {
        navigator.share({
            title: 'Cảnh báo lừa đảo - MindGuard',
            text: `Cảnh báo lừa đảo: ${identifier}. Kiểm tra ngay tại MindGuard!`,
            url: url
        }).catch(console.error);
    } else {
        navigator.clipboard.writeText(url)
            .then(() => alert('Đã sao chép link cảnh báo vào clipboard!'))
            .catch(err => console.error('Không thể copy link:', err));
    }
}

function followScammer() {
    if (!window.SCAMMER_DATA) return;
    
    // Check login just in case UI shows it by mistake
    if (!window.SCAMMER_DATA.isLoggedIn) {
        alert("Vui lòng đăng nhập để theo dõi.");
        return;
    }

    // Use originalIdentifier from SCAMMER_DATA which is available if logged in
    const identifier = window.SCAMMER_DATA.originalIdentifier;

    fetch('/scammer/follow', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'identifier=' + encodeURIComponent(identifier)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'followed') {
            updateFollowButton(true);
            // alert('Đã bắt đầu theo dõi!'); 
        } else if (data.status === 'unfollowed') {
            updateFollowButton(false);
            // alert('Đã hủy theo dõi.');
        } else {
            alert(data.message || 'Có lỗi xảy ra.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('K lỗi kết nối.');
    });
}

function updateFollowButton(isFollowing) {
    const btn = document.getElementById('btnFollowSidebar');
    const txt = document.getElementById('followTextSidebar');
    const icon = btn.querySelector('i');

    if (isFollowing) {
        btn.classList.remove('btn-outline-warning');
        btn.classList.add('btn-warning');
        icon.classList.remove('fa-bell-slash');
        icon.classList.add('fa-bell');
        txt.textContent = 'Đang theo dõi';
    } else {
        btn.classList.remove('btn-warning');
        btn.classList.add('btn-outline-warning');
        icon.classList.remove('fa-bell');
        icon.classList.add('fa-bell-slash');
        txt.textContent = 'Theo dõi cảnh báo';
    }
}

    }
}
