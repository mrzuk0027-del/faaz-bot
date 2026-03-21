from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__)
CORS(app)

# 🔥 DEBUG: check API key
print("API KEY LOADED:", os.getenv("GROQ_API_KEY"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(user_input):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # 🔥 use this for now
            messages=[{"role": "user", "content": user_input}],
            max_tokens=200
        )
        return response.choices[0].message.content

    except Exception as e:
        print("FULL ERROR:", str(e))
        return f"ERROR: {str(e)}"   # 👈 SHOWS REAL ERROR


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    reply = get_ai_response(user_input)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)