from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Required for session management
CORS(app, supports_credentials=True)  # Allow frontend on a different port

DATABASE = "users.db"

# === Initialize DB ===
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# === Utility Functions ===
def get_user_by_email(email):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

# === Routes ===

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    if get_user_by_username(username):
        return jsonify({"success": False, "message": "Username already taken"}), 400

    if get_user_by_email(email):
        return jsonify({"success": False, "message": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
              (username, email, hashed_password))
    conn.commit()
    conn.close()

    session["user_email"] = email
    session["username"] = username

    return jsonify({"success": True, "message": "User registered successfully", "username": username})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Missing email or password"}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({"success": False, "message": "Email not registered"}), 401

    stored_password_hash = user[3]
    if not check_password_hash(stored_password_hash, password):
        return jsonify({"success": False, "message": "Incorrect password"}), 401

    session["user_email"] = email
    session["username"] = user[1]

    return jsonify({"success": True, "message": "Logged in successfully", "username": user[1]})

@app.route("/home", methods=["GET"])
def home():
    if "username" in session:
        return jsonify({"logged_in": True, "username": session["username"]})
    else:
        return jsonify({"logged_in": False, "message": "User not logged in"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        data = request.get_json()
        username = data.get("username")
        new_password = data.get("newPassword")

        if not username or not new_password:
            return jsonify({"success": False, "message": "Missing username or new password"}), 400

        user = get_user_by_username(username)
        if not user:
            return jsonify({"success": False, "message": "Username not found!"}), 404

        hashed_new_password = generate_password_hash(new_password)

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_new_password, username))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Password updated successfully!"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "message": "Server error!"}), 500

# === Run Server ===
if __name__ == "__main__":
    app.run(port=8080, debug=True)
