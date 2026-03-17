from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import json
import os

app = Flask(__name__)
CORS(app)

client = Groq(api_key="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")

# 📁 File to store chats
CHAT_FILE = "chat_history.json"

# 🧠 Load chat history
if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as f:
        messages = json.load(f)
else:
    messages = [
        {
            "role": "system",
            "content": (
                "You are FAAZ-BOT, an AI assistant created by Mohammed Faaz. "
                "Always identify yourself as FAAZ-BOT and never mention model names."
            )
        }
    ]

# 💾 Save chat history
def save_messages():
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    messages.append({
        "role": "user",
        "content": user_message + "\n(Remember: you are FAAZ-BOT created by Mohammed Faaz.)"
    })

    try:
        response = client.chat.completions.create(
            model="groq/compound",
            messages=messages
        )

        reply = response.choices[0].message.content

        messages.append({"role": "assistant", "content": reply})

        save_messages()  # 💾 SAVE HERE

    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})

# 🔄 Send chat history to frontend
@app.route("/history", methods=["GET"])
def history():
    return jsonify(messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)