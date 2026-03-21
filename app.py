from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(user_input):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are FAAZ-BOT 🤖 created by Mohammed Faaz. You are smart, friendly, and helpful. Never say you are Llama or Meta AI."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Error:", str(e))
        return "⚠️ AI is temporarily unavailable. Try again."


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"reply": "Type something..."})

    reply = get_ai_response(user_input)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)