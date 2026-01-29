"""Helper functions for MindGuard application."""
import random
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    """
    Decorator: Bắt buộc đăng nhập User.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra xem email user có trong session không
        if not session.get('registration_email'):
            flash("Bạn cần đăng nhập để sử dụng tính năng này!", "warning")
            # Lưu lại trang người dùng muốn vào để chuyển hướng lại sau khi login
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator: Bắt buộc đăng nhập Admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash("Cần quyền quản trị để truy cập.", "danger")
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Các hàm phụ trợ khác giữ nguyên
def generate_certificate_code() -> str:
    return f"MG-{random.randint(100000, 999999)}"

def generate_session_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = random.randint(1000, 9999)
    return f"CHAT-{timestamp}-{random_part}"

def calculate_danger_level(report_count: int) -> str:
    if report_count >= 20: return 'critical'
    elif report_count >= 10: return 'high'
    elif report_count >= 5: return 'medium'
    else: return 'low'

def mask_sensitive_data(data: str, data_type: str = 'auto') -> str:
    """
    Mask thông tin nhạy cảm như SĐT, STK.
    VD: 0912345678 -> 091***5678
        123456789012 -> 1234***9012
    """
    if not data or len(data) < 4:
        return data
    
    # Auto-detect type
    if data_type == 'auto':
        data_clean = data.replace(' ', '').replace('-', '')
        if data_clean.isdigit():
            if len(data_clean) == 10 and data_clean.startswith('0'):
                data_type = 'phone'
            elif len(data_clean) >= 10:
                data_type = 'account'
    
    # Phone: 091***5678
    if data_type == 'phone':
        if len(data) >= 7:
            return f"{data[:3]}***{data[-4:]}"
    
    # Account/STK: 1234***9012
    if data_type == 'account':
        if len(data) >= 8:
            return f"{data[:4]}***{data[-4:]}"
    
    # Default: show first 4 and last 3
    if len(data) >= 8:
        return f"{data[:4]}***{data[-3:]}"
    
    return data[:2] + '***'

def calculate_risk_score(report_count: int, confirmed_count: int = 0, 
                         has_evidence: bool = False, days_since_first: int = 0) -> int:
    """
    Tính điểm rủi ro từ 0-100 dựa trên nhiều yếu tố.
    
    Args:
        report_count: Số lần báo cáo
        confirmed_count: Số người xác nhận
        has_evidence: Có bằng chứng không
        days_since_first: Số ngày từ báo cáo đầu
    
    Returns:
        Risk score (0-100)
    """
    score = 0
    
    # Base score from report count (max 40 points)
    if report_count >= 20:
        score += 40
    elif report_count >= 10:
        score += 35
    elif report_count >= 5:
        score += 25
    elif report_count >= 3:
        score += 15
    else:
        score += 5
    
    # Confirmed by community (max 25 points)
    if confirmed_count >= 10:
        score += 25
    elif confirmed_count >= 5:
        score += 20
    elif confirmed_count >= 2:
        score += 10
    elif confirmed_count >= 1:
        score += 5
    
    # Has evidence (max 20 points)
    if has_evidence:
        score += 20
    
    # Time factor (max 15 points) - càng gần đây càng nguy hiểm
    if days_since_first <= 7:
        score += 15
    elif days_since_first <= 30:
        score += 10
    elif days_since_first <= 90:
        score += 5
    
    return min(score, 100)

def get_verification_badge(status: str) -> dict:
    """
    Trả về badge HTML cho trạng thái xác minh.
    
    Returns:
        dict với 'text', 'class', 'icon'
    """
    badges = {
        'verified': {
            'text': 'Đã xác minh',
            'class': 'success',
            'icon': 'fa-check-circle'
        },
        'pending': {
            'text': 'Đang xác minh',
            'class': 'warning',
            'icon': 'fa-clock'
        },
        'unverified': {
            'text': 'Chưa xác minh',
            'class': 'secondary',
            'icon': 'fa-question-circle'
        }
    }
    return badges.get(status, badges['unverified'])

def get_risk_level_info(risk_score: int) -> dict:
    """
    Trả về thông tin về mức độ rủi ro dựa trên điểm.
    
    Returns:
        dict với 'level', 'color', 'text', 'icon'
    """
    if risk_score >= 80:
        return {
            'level': 'critical',
            'color': 'danger',
            'text': 'CỰC KỲ NGUY HIỂM',
            'icon': 'fa-exclamation-triangle'
        }
    elif risk_score >= 60:
        return {
            'level': 'high',
            'color': 'warning',
            'text': 'RỦI RO CAO',
            'icon': 'fa-exclamation-circle'
        }
    elif risk_score >= 40:
        return {
            'level': 'medium',
            'color': 'info',
            'text': 'CẨN THẬN',
            'icon': 'fa-info-circle'
        }
    else:
        return {
            'level': 'low',
            'color': 'secondary',
            'text': 'RỦI RO THẤP',
            'icon': 'fa-shield-alt'
        }