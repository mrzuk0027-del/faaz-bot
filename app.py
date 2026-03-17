from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# 🔐 API KEY (from Render environment)
GROQ_API_KEY = os.getenv("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")

# 💾 Memory file
HISTORY_FILE = "chat_history.json"

# Load history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

# Save history
def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

# 🌐 Serve frontend
@app.route("/")
def home():
    return send_file("index.html")

# 📜 Get history
@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(load_history())

# 💬 Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "").strip()
        if not user_message:
            return jsonify({"reply": "Please type something."})

        history = load_history()

        # 🧠 SYSTEM PROMPT
        messages = [
            {
                "role": "system",
                "content": (
                    "You are FAAZ-BOT, a smart and friendly AI assistant created by Mohammed Faaz. "
                    "Do NOT mention model names like Groq, LLaMA, Compound, etc. "
                    "ONLY say you are FAAZ-BOT created by Mohammed Faaz if the user asks who you are. "
                    "Otherwise respond naturally, clearly, and helpfully."
                )
            }
        ]

        messages += history
        messages.append({"role": "user", "content": user_message})

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "groq/compound",
                "messages": messages
            },
            timeout=30
        )

        data = response.json()

        # 🛑 Handle API errors safely
        if "choices" not in data:
            print("API ERROR:", data)
            return jsonify({"reply": "⚠️ AI is temporarily unavailable."})

        bot_reply = data["choices"][0]["message"]["content"]

        # Save memory
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": bot_reply})
        save_history(history)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("SERVER ERROR:", str(e))
        return jsonify({"reply": "⚠️ Server error occurred."})

# 🚀 Run app (Render compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)