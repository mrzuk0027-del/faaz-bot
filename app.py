from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("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")

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    history = load_history()

    messages = [
        {
            "role": "system",
            "content": (
                "You are FAAZ-BOT, a smart and friendly AI assistant created by Mohammed Faaz. "
                "Never mention any model names like Groq, LLaMA, Compound, etc. "
                "Only say you are FAAZ-BOT created by Mohammed Faaz if the user asks who you are or who created you. "
                "Otherwise respond normally in a clean, natural way."
            )
        }
    ]

    messages += history
    messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {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}",
                "Content-Type": "application/json"
            },
            json={
                "model": "groq/compound",  # ✅ YOUR WORKING MODEL
                "messages": messages
            }
        )

        data = response.json()

        bot_reply = data["choices"][0]["message"]["content"]

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": bot_reply})
        save_history(history)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(load_history())

@app.route("/")
def home():
    return "FAAZ-BOT is running 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)