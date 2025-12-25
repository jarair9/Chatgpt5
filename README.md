# 🧠 Claila GPT-5 API Proxy

> **A high-performance, stateless API wrapper for the Claila GPT-5 Mini model.**

This project allows you to interact with the Claila AI (GPT-5 Mini) programmatically. It wraps the internal API logic into a standard REST endpoint, handles session management automatically, and is optimized for serverless deployment (Vercel).

---

## ✨ Key Features

-   **🚀 Stateless & Serverless**: Designed to run on Vercel, AWS Lambda, or simple Docker containers.
-   **⚡ Session Optimization**: Smart caching of cookies and CSRF tokens to reduce latency by ~60% on subsequent requests.
-   **🌍 CORS Enabled**: Fully configured for Cross-Origin Resource Sharing. You can call this API directly from your frontend (React, Vue, etc.) without a backend.
-   **🤖 System Prompts**: Supports custom system instructions to define the AI's persona and behavior.
-   **🔒 Automatic Spoofing**: Handles all necessary headers, cookies, and user-agent rotation to mimic legitimate browser traffic.

---

## 🛠️ Installation & Local Development

### Prerequisites
-   Python 3.9+
-   `pip` (Python Package Manager)

### Steps
1.  **Clone the repository** (if applicable) or download the source.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Start the Server**:
    ```bash
    python app.py
    ```
    The server will start at `http://localhost:5000`.

---

## ☁️ Deployment

### Option A: Vercel (Recommended)
This method is free and requires zero maintenance.

1.  **Install Vercel CLI**: `npm i -g vercel`
2.  **Login**: `vercel login`
3.  **Deploy**: Run the following command in the project root:
    ```bash
    vercel
    ```
4.  **Done!** You will receive a URL like: `https://your-project-name.vercel.app`

### Option B: Docker / Other Providers
Since this is a standard Flask app, you can deploy it anywhere.
-   **Command**: `gunicorn app:app`
-   **Port**: Defaults to 5000 (configurable via environment).

---

## 📖 API Reference

### **POST** `/chat`
Sends a message to the AI.

#### **Request Headers**
| Header | Value | Required |
| :--- | :--- | :--- |
| `Content-Type` | `application/json` | ✅ Yes |

#### **Request Body (JSON)**
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `string` | ✅ Yes | The user's input/question. |
| `system_prompt` | `string` | ❌ No | Instructions to guide the AI's behavior (e.g., "Answer in French"). |

#### **Example Request**
```bash
curl -X POST https://your-app.vercel.app/chat \
     -H "Content-Type: application/json" \
     -d '{
           "message": "Explain black holes.",
           "system_prompt": "You are a famous astrophysicist."
         }'
```

#### **Success Response (200 OK)**
```json
{
  "response": "A black hole is a region of spacetime where gravity is so strong that nothing..."
}
```

#### **Error Response (503 Service Unavailable)**
```json
{
  "error": "Failed to initialize session. Upstream API may be down."
}
```

---

## ⚙️ Architecture Details

### Session Reuse Logic
To speed up responses, the application implements a `ChatSession` class:
1.  **First Request**: The app fetches a fresh CSRF token and Session ID from Claila. This takes ~1-2 seconds.
2.  **Subsequent Requests**: The app reuses these credentials. Latency drops to just the AI processing time.
3.  **Token Expiry**: If a request fails with a 401/403/CSRF error, the app automatically fetches a fresh token and retries the request transparently.

---

## ❓ Troubleshooting

### "Request timed out"
-   The upstream AI model might be under heavy load. The default timeout is set to 30 seconds.
-   **Fix**: Retry the request.

### "Failed to initialize session"
-   The upstream service (`app.claila.com`) might be down or blocking the generated User-Agents.
-   **Fix**: Check if `app.claila.com` is accessible in your browser.

### CORS Errors on Localhost
-   Ensure you are accessing `http://127.0.0.1:5000` and not `localhost` if your frontend requires specific origin matching, although `flask-cors` is set to accept `*`.
