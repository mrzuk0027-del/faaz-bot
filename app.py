from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from groq import Groq

app = Flask(__name__)

# ---------------- CONFIG ---------------- #
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- DATABASE ---------------- #
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        response TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- AI FUNCTION ---------------- #
def get_ai_response(user_input):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
    {
        "role": "system",
        "content": (
            "You are FAAZ-BOT created by Mohammed Faaz.\n"
            "You MUST follow these rules strictly:\n"
            "- Never say you are created by Meta, OpenAI, or any company.\n"
            "- Never mention Llama.\n"
            "- If asked who created you, say ONLY: 'I was created by Mohammed Faaz.'\n"
            "- If asked your name, say ONLY: 'I am FAAZ-BOT.'\n"
            "- For all other questions, answer normally without introducing yourself.\n"
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
        print("AI ERROR:", e)
        return "⚠️ AI is temporarily unavailable. Please try again."

# ---------------- ROUTES ---------------- #
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/chatpage")
def chatpage():
    return render_template("index.html")

# ---------------- REGISTER ---------------- #
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    try:
        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (data["username"], data["password"]))

        conn.commit()
        conn.close()

        return jsonify({"status": "registered"})

    except:
        return jsonify({"status": "error", "message": "User already exists"})

# ---------------- LOGIN ---------------- #
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (data["username"], data["password"]))

    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "user_id": user[0]})
    else:
        return jsonify({"status": "fail"})

# ---------------- CHAT ---------------- #
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    user_id = data.get("user_id", 1)

    if not user_input:
        return jsonify({"reply": "Please type something."})

    reply = get_ai_response(user_input)

    try:
        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        c.execute(
            "INSERT INTO messages (user_id, message, response) VALUES (?, ?, ?)",
            (user_id, user_input, reply)
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)

    return jsonify({"reply": reply})

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
