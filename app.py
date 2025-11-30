from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import openai
import os
import traceback
from dotenv import load_dotenv  # <-- NEW

load_dotenv()  # <-- NEW

OPENAI_API_KEY = os.getenv("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")  # <-- NEW
openai.api_key = "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" # <-- NEW

app = Flask(__name__)
app.secret_key = 'change_this_to_a_secret_key'

# ---------- CONFIG ----------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "admin123"    # <-- replace with your MySQL password
DB_NAME = "mental_health_ai"


# ----------------------------

# ---------- MySQL connection ----------
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = db.cursor(dictionary=True)
# --------------------------------------

# Helper for chat session messages
def append_message(sender, text):
    msgs = session.get('chat_messages', [])
    msgs.append({'sender': sender, 'text': text})
    if len(msgs) > 60:
        msgs = msgs[-60:]
    session['chat_messages'] = msgs

# Routes
@app.route('/')
def home():
    return redirect(url_for('register'))

from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
import traceback

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        # Check DB for existing email
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing = cursor.fetchone()

        if existing:
            flash("Email already exists! Please login or use another email.", "error")
            return render_template("register.html", name=name, email=email)

        try:
            hashed = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed)
            )
            db.commit()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            print("Error:", e)
            traceback.print_exc()
            flash("Something went wrong. Try again.", "error")
            return render_template("register.html", name=name, email=email)

    return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        password_input = request.form.get('password','').strip()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password_input):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['chat_messages'] = []
            flash(f"Welcome, {user['name']}!")
            return redirect(url_for('chat'))
        flash("Invalid credentials.")
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        flash("Please login first.")
        return redirect(url_for('login'))
    return render_template('chat.html', user_name=session.get('user_name','User'))

# --- AI chat endpoint ---
@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'user_id' not in session:
        return jsonify({'error':'not authenticated'}), 401

    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'error':'empty message'}), 400

    append_message('You', message)

    # Call OpenAI API
    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a supportive mental health assistant."},
                {"role": "user", "content": message}
            ]
        )
        ai_text = response.choices[0].message.content.strip()
    except Exception as e:
        print("🔥 OpenAI Error:", e)
        ai_text = "Sorry, something went wrong with AI response."

    append_message('AI', ai_text)
    return jsonify({'reply': ai_text})

@app.route('/api/get_chats')
def api_get_chats():
    if 'user_id' not in session:
        return jsonify({'error':'not authenticated'}), 401
    return jsonify(session.get('chat_messages', []))

# Run app
if __name__ == '__main__':
    app.run(debug=True)
