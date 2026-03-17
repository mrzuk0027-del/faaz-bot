from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# 🔐 Get API key from environment (SAFE)
GROQ_API_KEY = os.getenv("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")

HISTORY_FILE = "chat_history.json"

# Load chat history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

# Save chat history
def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

@app.route("/")
def home():
    return "FAAZ-BOT is running 🚀"

@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(load_history())

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
                    "You are FAAZ-BOT, a helpful AI created by Mohammed Faaz. "
                    "Do NOT mention any model names (like Groq, LLaMA, Compound). "
                    "Only say your name and creator if the user asks. "
                    "Otherwise respond naturally and clearly."
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
            return jsonify({"reply": "⚠️ AI is temporarily unavailable. Try again."})

        bot_reply = data["choices"][0]["message"]["content"]

        # Save memory
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": bot_reply})
        save_history(history)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("SERVER ERROR:", str(e))
        return jsonify({"reply": "⚠️ Server error occurred."})

# ✅ IMPORTANT for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)