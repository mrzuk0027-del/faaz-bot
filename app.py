from flask import Flask, request, jsonify, render_template
import sqlite3
from groq import Groq
import os

app = Flask(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- DATABASE ---------------- #
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
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

# ---------------- AI ---------------- #
def get_ai_response(user_input):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are FAAZ-BOT created by Mohammed Faaz."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

# ---------------- ROUTES ---------------- #
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/chatpage")
def chatpage():
    return render_template("index.html")

# -------- REGISTER -------- #
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
              (data["username"], data["password"]))

    conn.commit()
    conn.close()

    return jsonify({"status": "registered"})

# -------- LOGIN -------- #
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

# -------- CHAT -------- #
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data["message"]
    user_id = data.get("user_id", 1)

    reply = get_ai_response(user_input)

    # Save to DB
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, message, response) VALUES (?, ?, ?)",
              (user_id, user_input, reply))
    conn.commit()
    conn.close()

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
