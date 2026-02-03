"""Chatbot AI logic utilities."""
import json
import urllib.request
import urllib.error
from config import Config

def query_ai_model(prompt, system_prompt=None):
    """Query OpenRouter AI with automatic fallback."""
    api_key = Config.OPENROUTER_API_KEY
    models = Config.OPENROUTER_MODELS
    
    if not api_key or api_key.startswith("sk-or-v1-..."):
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mindguard.local",
        "X-Title": "MindGuard"
    }
    
    if system_prompt is None:
        system_prompt = "Bạn là MindGuard AI, chuyên gia an ninh mạng. Hãy trả lời ngắn gọn, súc tích về các vấn đề lừa đảo trực tuyến."

    for model in models:
        data = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
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
    """Fallback logic if AI fails or for simple checks."""
    msg = message.lower()
    if "lừa đảo" in msg or "scam" in msg:
        return "Đây có thể là dấu hiệu lừa đảo. Hãy kiểm tra kỹ thông tin người gửi và không chuyển tiền."
    return "Tôi chưa rõ ý bạn. Bạn có thể cung cấp thêm chi tiết tin nhắn nghi ngờ không?"

def generate_support_reply(message):
    """Specific reply for support context."""
    ai_reply = query_ai_model(message, system_prompt="Bạn là trợ lý hỗ trợ báo cáo lừa đảo. Hãy hướng dẫn người dùng cách tố cáo.")
    return ai_reply if ai_reply else simple_bot_reply(message)