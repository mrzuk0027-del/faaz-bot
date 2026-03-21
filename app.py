from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.getenv("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"))

# Function to get AI response (NO MEMORY)
def get_ai_response(user_input):
    try:
        # Primary model (smart)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are FAAZ-BOT created by Mohammed Faaz. Be helpful, smart, and friendly."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Primary model failed:", e)

        try:
            # Fallback model (fast)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are FAAZ-BOT created by Mohammed Faaz. Be helpful and friendly."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content

        except Exception as e:
            print("Fallback failed:", e)
            return "⚠️ AI is temporarily unavailable. Please try again later."


# API route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"reply": "Please send a message."})

    reply = get_ai_response(user_input)

    return jsonify({"reply": reply})


# Root route
@app.route("/")
def home():
    return "FAAZ-BOT is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)