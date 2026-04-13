"""Chatbot AI logic utilities."""
import json
import urllib.request
import urllib.error
from config import Config

# Từ khóa nhạy cảm cần chuyển sang câu trả lời an toàn
_SENSITIVE_KEYWORDS = [
    "chính trị", "đảng", "chính phủ", "biểu tình", "tôn giáo", "phật giáo",
    "thiên chúa", "hồi giáo", "nhà nước", "quốc hội", "bầu cử", "lật đổ",
    "phản động", "khủng bố", "vũ khí", "ma túy",
]

_SAFE_FALLBACK = (
    "Hiện tại MindGuard chưa đủ dữ liệu để kết luận chắc chắn về vấn đề này. "
    "Để an toàn, bác/anh/chị tuyệt đối KHÔNG cung cấp mã OTP, mật khẩu hay chuyển tiền. "
    "Nếu cần hỗ trợ khẩn, hãy liên hệ đường dây nóng Công an TP Hà Nội: 113."
)

SYSTEM_PROMPT_DEFAULT = """Bạn là MindGuard AI, trợ lý cảnh báo lừa đảo của người dân Hà Nội.

Quy tắc bắt buộc:
1. Dùng ngôn ngữ đời thường, gần gũi. Xưng hô "bác/anh/chị" với người dùng.
2. Tránh tuyệt đối thuật ngữ kỹ thuật. Ví dụ: KHÔNG nói "malware" — hãy nói "mã độc ăn cắp tài khoản ngân hàng".
3. Câu trả lời ngắn gọn, tối đa 3-4 câu. Nếu cần liệt kê thì dùng gạch đầu dòng.
4. Nếu không chắc chắn hoặc câu hỏi ngoài phạm vi lừa đảo/an toàn mạng, hãy trả lời: "MindGuard chưa có đủ thông tin để kết luận. Để an toàn, bác/anh/chị không nên cung cấp OTP hay chuyển tiền. Liên hệ 113 nếu cần hỗ trợ khẩn."
5. KHÔNG đưa ra kết luận pháp lý, KHÔNG khuyên dùng thuốc, KHÔNG bình luận chính trị hay tôn giáo."""


def _is_sensitive(message: str) -> bool:
    """Kiểm tra câu hỏi có chứa nội dung nhạy cảm không."""
    msg_lower = message.lower()
    return any(kw in msg_lower for kw in _SENSITIVE_KEYWORDS)


def query_ai_model(prompt, system_prompt=None):
    """Query OpenRouter AI with automatic fallback."""
    api_key = Config.OPENROUTER_API_KEY
    models = Config.OPENROUTER_MODELS

    if not api_key or api_key.startswith("sk-or-v1-..."):
        return None

    # Chặn câu hỏi nhạy cảm trước khi gọi AI
    if _is_sensitive(prompt):
        return _SAFE_FALLBACK

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mindguard.local",
        "X-Title": "MindGuard"
    }

    if system_prompt is None:
        system_prompt = SYSTEM_PROMPT_DEFAULT

    for model in models:
        data = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                result = json.loads(response.read().decode('utf-8'))
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"Model {model} HTTP error {e.code}: {error_body}")
            continue
        except Exception as e:
            print(f"Model {model} failed: {e}")
            continue

    return None


def simple_bot_reply(message):
    """Fallback khi AI không khả dụng."""
    if _is_sensitive(message):
        return _SAFE_FALLBACK

    msg = message.lower()
    if any(kw in msg for kw in ["lừa đảo", "scam", "giả mạo", "link lạ", "đường link"]):
        return (
            "Đây có thể là dấu hiệu lừa đảo. "
            "Bác/anh/chị KHÔNG bấm vào link lạ, KHÔNG cung cấp OTP hay mật khẩu. "
            "Có thể báo cáo ngay tại mục 'Tố cáo lừa đảo' trên MindGuard."
        )
    if any(kw in msg for kw in ["otp", "mã xác nhận", "mã ngân hàng"]):
        return (
            "TUYỆT ĐỐI không cung cấp mã OTP cho bất kỳ ai, kể cả người tự xưng là nhân viên ngân hàng hay công an. "
            "Đây là chiêu lừa đảo phổ biến nhất hiện nay."
        )
    if any(kw in msg for kw in ["chuyển tiền", "chuyển khoản", "nạp tiền"]):
        return (
            "Bác/anh/chị hãy xác minh kỹ danh tính người nhận trước khi chuyển tiền. "
            "Nếu bị yêu cầu chuyển tiền gấp hoặc giữ bí mật — đó là dấu hiệu lừa đảo."
        )
    return (
        "MindGuard chưa đủ thông tin để trả lời câu này. "
        "Bác/anh/chị có thể mô tả thêm nội dung tin nhắn hoặc đường link nghi ngờ không?"
    )


def generate_support_reply(message):
    """Trả lời trong modal hỗ trợ báo cáo lừa đảo."""
    support_prompt = (
        "Bạn là trợ lý hỗ trợ báo cáo lừa đảo của MindGuard. "
        "Hướng dẫn người dùng cách tố cáo bằng ngôn ngữ đơn giản, thân thiện. "
        "Xưng hô bác/anh/chị. Tối đa 3 câu."
    )
    ai_reply = query_ai_model(message, system_prompt=support_prompt)
    return ai_reply if ai_reply else simple_bot_reply(message)