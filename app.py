from flask import Flask, request, jsonify, render_template
from groq import Groq
import os

app = Flask(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- AI FUNCTION ---------------- #
def get_ai_response(user_input):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are FAAZ-BOT, a smart and helpful AI assistant. "
                        "Never say you are created by Meta or any company. "
                        "If asked who created you, say: 'I was created by Mohammed Faaz.' "
                        "Otherwise, respond normally without introducing yourself."
                    )
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
        print("ERROR:", e)
        return "⚠️ AI is temporarily unavailable."

# ---------------- ROUTES ---------------- #
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

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
