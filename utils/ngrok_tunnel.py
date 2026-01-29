import os
import json
import sys
from pyngrok import ngrok, conf

def start_ngrok(app_port=5000):
    """
    Initialize ngrok tunnel checking .env/ngrok.json
    """
    # 1. Try to find token in environment
    token = os.environ.get("NGROK_AUTHTOKEN")
    
    # 2. If not in env, check .env/ngrok.json
    if not token:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        token_path = os.path.join(base_dir, '.env', 'ngrok.json')
        
        if os.path.exists(token_path):
            try:
                with open(token_path, 'r') as f:
                    data = json.load(f)
                    token = data.get("NGROK_AUTHTOKEN")
            except Exception as e:
                print(f"⚠️  Could not read ngrok token from {token_path}: {e}")
    
    if token:
        print(f"✔️  Found ngrok authentication token.") # Silent this
        conf.get_default().auth_token = token
        
        # Open a HTTP tunnel on the default port 5000
        try:
            # Kill existing tunnels to avoid issues
            ngrok.kill()
            
            # Start new tunnel
            public_url = ngrok.connect(app_port).public_url
            # print(f"🌍 Public URL: {public_url}") # Silent this, let app.py handle printing
            return public_url
        except Exception as e:
            print(f"❌ Error starting ngrok tunnel: {e}")
            return None
    else:
        print("⚠️  No NGROK_AUTHTOKEN found in environment or .env/ngrok.json")
        return None
