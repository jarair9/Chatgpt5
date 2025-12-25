from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import json
import random
import string
from datetime import datetime

app = Flask(__name__)
CORS(app) # Enable CORS for all routes and origins

# --- Helper Functions ---

def rand_string(n=16):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def rand_useragent():
    versions = ["124.0.0.0", "125.0.0.0", "126.0.0.0", "127.0.0.0", "128.0.0.0", "129.0.0.0", "130.0.0.0"]
    platforms = [
        f"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(versions)} Mobile Safari/537.36",
        f"Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(versions)} Mobile Safari/537.36",
        f"Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(versions)} Mobile Safari/537.36",
        f"Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(versions)} Mobile Safari/537.36",
    ]
    return random.choice(platforms)

def generate_cookies():
    return {
        'dmcfkjn3cdc': rand_string(32),
        '_ga': f"GA1.1.{random.randint(100000,999999)}.{random.randint(1000000000,1999999999)}",
        '_gid': f"GA1.1.{random.randint(100000000,999999999)}.{int(time.time())}",
        'theme': 'dark',
        'lang': 'en',
        'auh': rand_string(8),
        'session_id': rand_string(24),
    }

def generate_headers():
    return {
        'authority': 'app.claila.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://app.claila.com',
        'referer': 'https://app.claila.com/chat?uid=' + rand_string(8) + '&lang=en',
        'user-agent': rand_useragent(),
        'x-requested-with': 'XMLHttpRequest',
    }

API_TOKEN = "https://app.claila.com/api/v2/getcsrftoken"
API_CHAT = "https://app.claila.com/api/v2/unichat4"

def get_token(cookies, headers):
    try:
        r = requests.get(API_TOKEN, cookies=cookies, headers=headers, timeout=10)
        return r.text.strip()
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

# --- Session Management ---

class ChatSession:
    def __init__(self):
        self.cookies = None
        self.headers = None
        self.csrf_token = None
        self.last_refresh_time = 0

    def get_valid_session(self, force_refresh=False):
        # Refresh if forced or never initialized
        if force_refresh or not self.csrf_token:
            print("[INFO] Refreshing session tokens...")
            self.cookies = generate_cookies()
            self.headers = generate_headers()
            self.csrf_token = get_token(self.cookies, self.headers)
            if self.csrf_token:
                self.headers["x-csrf-token"] = self.csrf_token
                self.last_refresh_time = time.time()
                print(f"[INFO] New token: {self.csrf_token[:10]}...")
                return True
            print("[ERROR] Failed to get CSRF token")
            return False
        return True

session_store = ChatSession()

# --- Routes ---

@app.route('/')
def index():
    return jsonify({"status": "online", "message": "Claila API Proxy is running. Send POST requests to /chat."})

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    system_prompt = request.json.get('system_prompt', '') # Optional system prompt
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Ensure valid session
    if not session_store.get_valid_session():
        return jsonify({'error': 'Failed to initialize session. Upstream API may be down.'}), 503

    # Prepare Payload
    # Concatenate system prompt if provided
    if system_prompt:
        full_message = f"[SYSTEM: {system_prompt}] [USER: {user_message}] [RESPOND IN ENGLISH ONLY]"
    else:
        full_message = f"[RESPOND IN ENGLISH ONLY] {user_message}"
    
    data = {
        'model': 'gpt-5-mini',
        'calltype': 'completion',
        'message': full_message,
        'sessionId': rand_string(12),
        'chat_mode': 'chat',
        'websearch': 'false',
        'tmp_enabled': '0',
        'lang': 'en',
        'language': 'english',
    }

    def attempt_request():
        return requests.post(API_CHAT, cookies=session_store.cookies, headers=session_store.headers, data=data, timeout=30)

    try:
        # First attempt
        resp = attempt_request()
        
        # Check for specific failure modes that suggest session expiry
        # 403 Forbidden, 419 Page Expired (Laravel), etc.
        # Or if the response contains "CSRF" error message
        needs_refresh = False
        if resp.status_code in [401, 403, 419]:
            needs_refresh = True
        elif resp.status_code == 200 and "csrf" in resp.text.lower() and "token" in resp.text.lower():
            needs_refresh = True
            
        if needs_refresh:
            print("[INFO] Session invalid or expired. Refreshing for retry...")
            if session_store.get_valid_session(force_refresh=True):
                resp = attempt_request()
            else:
                 return jsonify({'error': 'Session refresh failed after expiry.'}), 503

        resp_text = resp.text

        try:
            j = json.loads(resp_text)
            reply = j.get("response", resp_text)
        except json.JSONDecodeError:
            reply = resp_text

        return jsonify({'response': reply})

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
