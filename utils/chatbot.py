"""Chatbot AI logic utilities."""
import json
import re
import urllib.error
import urllib.request

from config import Config


DEFAULT_SYSTEM_PROMPT = (
    "Bạn là MindGuard AI, trợ lý an ninh mạng cho người dùng Việt Nam. "
    "Luôn trả lời bằng tiếng Việt tự nhiên, rõ ràng, ngắn gọn và hữu ích. "
    "Khi người dùng nghi bị lừa đảo, hãy ưu tiên các bước xử lý ngay, cảnh báo rủi ro và cách lưu bằng chứng. "
    "Không bịa thông tin, không nói lan man, không dùng từ vô nghĩa."
)

SUPPORT_SYSTEM_PROMPT = (
    "Bạn là trợ lý hỗ trợ báo cáo lừa đảo của MindGuard. "
    "Hướng dẫn người dùng các bước tố cáo, lưu bằng chứng và tự bảo vệ tài khoản bằng tiếng Việt rõ ràng."
)

LOW_QUALITY_MARKERS = (
    "tham comand",
    "mật khan",
    "diện tích khác",
    "giấi",
    "thiến một",
    "trào phản ứng",
    "phê phát",
    "hang drồn",
    "li̱n",
)


def normalize_ai_reply(text):
    """Collapse whitespace so provider output can be evaluated consistently."""
    return re.sub(r"\s+", " ", (text or "")).strip()


def is_low_quality_ai_reply(text):
    """Reject obviously broken provider output before surfacing it to users."""
    normalized = normalize_ai_reply(text)
    if len(normalized) < 40:
        return True

    lowered = normalized.lower()
    if any(marker in lowered for marker in LOW_QUALITY_MARKERS):
        return True

    repeated_words = re.search(r"\b([\wÀ-ỹ]{4,})\s+\1\b", lowered)
    if repeated_words:
        return True

    return False


def query_ai_model_with_meta(prompt, system_prompt=None):
    """Query OpenRouter and return both reply text and provider metadata."""
    api_key = Config.OPENROUTER_API_KEY
    models = Config.OPENROUTER_MODELS
    meta = {
        "source": "fallback",
        "model": None,
        "errors": [],
    }

    if not api_key or api_key.startswith("sk-or-v1-..."):
        meta["errors"].append("openrouter_api_key_missing")
        return None, meta

    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mindguard.local",
        "X-Title": "MindGuard"
    }

    for model in models:
        payload = {
            "model": model,
            "temperature": 0.2,
            "max_tokens": 500,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode("utf-8"))
                choices = result.get("choices") or []
                if not choices:
                    meta["errors"].append(f"{model}:empty_choices")
                    continue

                content = normalize_ai_reply(choices[0].get("message", {}).get("content", ""))
                if is_low_quality_ai_reply(content):
                    meta["errors"].append(f"{model}:low_quality_response")
                    continue

                meta["source"] = "openrouter"
                meta["model"] = model
                return content, meta
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8")
            meta["errors"].append(f"{model}:http_{error.code}")
            print(f"Model {model} HTTP error {error.code}: {error_body}")
        except Exception as error:
            meta["errors"].append(f"{model}:{type(error).__name__}")
            print(f"Model {model} failed: {error}")

    return None, meta


def query_ai_model(prompt, system_prompt=None):
    """Backward-compatible string-only provider call."""
    reply, _meta = query_ai_model_with_meta(prompt, system_prompt=system_prompt)
    return reply


def simple_bot_reply(message):
    """Local safety fallback when provider output is unavailable or unusable."""
    msg = (message or "").lower()

    if any(keyword in msg for keyword in ["bị lừa tiền", "mất tiền", "chuyển khoản", "chuyển tiền", "chiếm đoạt", "mất otp"]):
        return (
            "Tình huống này có dấu hiệu lừa đảo tài chính. Bạn nên làm ngay:\n"
            "- Gọi ngân hàng hoặc ví điện tử để khóa tài khoản, thẻ và yêu cầu tra soát giao dịch.\n"
            "- Đổi mật khẩu email, ngân hàng, ví điện tử và bật xác thực 2 lớp nếu chưa có.\n"
            "- Ngừng chuyển thêm tiền, không gửi mã OTP, mật khẩu hay ảnh giấy tờ cho đối tượng.\n"
            "- Lưu toàn bộ bằng chứng: ảnh chụp màn hình, số tài khoản, link, tin nhắn, hóa đơn chuyển khoản.\n"
            "- Trình báo cơ quan công an hoặc ngân hàng càng sớm càng tốt để tăng khả năng xử lý."
        )

    if any(keyword in msg for keyword in ["otp", "mã xác minh", "mật khẩu", "đăng nhập"]):
        return (
            "Nếu bạn đã lộ OTP hoặc mật khẩu, hãy xử lý ngay:\n"
            "- Đổi mật khẩu của email, ngân hàng, mạng xã hội và các tài khoản liên quan.\n"
            "- Đăng xuất khỏi các phiên lạ và bật xác thực 2 lớp.\n"
            "- Kiểm tra lịch sử giao dịch hoặc đăng nhập bất thường để phát hiện chiếm quyền truy cập.\n"
            "- Không cung cấp thêm mã xác minh cho bất kỳ ai, kể cả người tự xưng là nhân viên hỗ trợ."
        )

    if any(keyword in msg for keyword in ["link", "website", "trang web", "url", "http"]):
        return (
            "Nếu bạn nghi ngờ link hoặc website lừa đảo:\n"
            "- Không bấm tiếp vào link và không nhập thông tin cá nhân hoặc thông tin thẻ.\n"
            "- Kiểm tra kỹ tên miền, lỗi chính tả và các dấu hiệu giả mạo thương hiệu.\n"
            "- Chụp màn hình trang nghi ngờ để lưu bằng chứng.\n"
            "- Bạn có thể gửi nguyên văn link hoặc nội dung tin nhắn cho tôi để tôi phân tích kỹ hơn."
        )

    if any(keyword in msg for keyword in ["tuyển dụng", "việc làm", "cộng tác viên", "nhiệm vụ", "hoa hồng"]):
        return (
            "Đây là mẫu lừa đảo tuyển dụng rất phổ biến nếu họ yêu cầu ứng tiền hoặc làm nhiệm vụ nhận hoa hồng.\n"
            "- Không nộp phí giữ chỗ, phí đào tạo hoặc tiền mở tài khoản nhiệm vụ.\n"
            "- Kiểm tra công ty qua website chính thức và kênh liên hệ độc lập.\n"
            "- Lưu lại thông tin tuyển dụng, số điện thoại và tài khoản nhận tiền để báo cáo khi cần."
        )

    if "lừa đảo" in msg or "scam" in msg or "báo cáo" in msg or "số điện thoại" in msg:
        return (
            "Đây có thể là dấu hiệu lừa đảo. Bạn nên:\n"
            "- Không chuyển tiền hoặc cung cấp thông tin cá nhân.\n"
            "- Kiểm tra người gửi, số điện thoại, tài khoản ngân hàng hoặc đường link.\n"
            "- Lưu bằng chứng để báo cáo trên MindGuard hoặc cho cơ quan chức năng nếu cần."
        )

    return (
        "Bạn hãy gửi thêm chi tiết như nội dung tin nhắn, đường link, số điện thoại hoặc cách đối tượng liên hệ. "
        "Trong lúc này, đừng bấm link lạ, đừng chuyển tiền và không chia sẻ mã OTP."
    )


def generate_chatbot_reply(message, system_prompt=None):
    """Return a user-facing reply plus source metadata."""
    ai_reply, meta = query_ai_model_with_meta(message, system_prompt=system_prompt)
    if ai_reply:
        return ai_reply, meta

    fallback_reply = simple_bot_reply(message)
    meta["source"] = "fallback"
    return fallback_reply, meta


def generate_support_reply(message):
    """Specific reply flow for support context."""
    return generate_chatbot_reply(message, system_prompt=SUPPORT_SYSTEM_PROMPT)