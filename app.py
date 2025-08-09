from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import os
import re
import threading

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Enable CORS (allow all origins for now)
CORS(app, supports_credentials=True)

EXCEL_FILE = "user_auth.xlsx"
file_lock = threading.Lock()  # To avoid race conditions on Excel file access

def fix_excel_schema():
    """
    Fix Excel file schema by:
    - Renaming 'password_hash' column to 'password'
    - Dropping unwanted columns if they exist
    """
    if os.path.exists(EXCEL_FILE):
        with file_lock:
            df = pd.read_excel(EXCEL_FILE)

            if "password_hash" in df.columns:
                df.rename(columns={"password_hash": "password"}, inplace=True)

            for col in ["id", "Unnamed: 4", "created_at"]:
                if col in df.columns:
                    df.drop(columns=[col], inplace=True)

            df.to_excel(EXCEL_FILE, index=False)
            print("Excel file schema fixed:", df.columns.tolist())
    else:
        print(f"{EXCEL_FILE} does not exist, skipping schema fix.")

def init_excel():
    """Create Excel file with headers if missing, then fix schema."""
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["username", "email", "password"])
        df.to_excel(EXCEL_FILE, index=False)
        print(f"{EXCEL_FILE} created with initial schema.")
    else:
        fix_excel_schema()

init_excel()

def read_users():
    """Read all users from Excel in a thread-safe way."""
    with file_lock:
        return pd.read_excel(EXCEL_FILE)

def save_users(df):
    """Save users DataFrame back to Excel safely."""
    with file_lock:
        df.to_excel(EXCEL_FILE, index=False)

def get_user_by_email(email):
    df = read_users()
    return df[df["email"].str.lower() == email.lower()]

def get_user_by_username(username):
    df = read_users()
    return df[df["username"].str.lower() == username.lower()]

def is_strong_password(password):
    """Check if password is strong (8+ chars, uppercase, lowercase, digit)."""
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password)
    )

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")  # Optional: your frontend HTML

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() if request.is_json else request.form
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not all([username, email, password]):
        return jsonify({"success": False, "message": "Please fill all fields"}), 400

    if not is_strong_password(password):
        return jsonify({"success": False, "message": "Password must be 8+ chars, include upper, lower, and number"}), 400

    if not get_user_by_username(username).empty:
        return jsonify({"success": False, "message": "Username already taken"}), 400

    if not get_user_by_email(email).empty:
        return jsonify({"success": False, "message": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    df = read_users()
    df.loc[len(df)] = [username, email, hashed_password]
    save_users(df)

    return jsonify({"success": True, "message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() if request.is_json else request.form
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not all([email, password]):
        return jsonify({"success": False, "message": "Please enter email and password"}), 400

    user_df = get_user_by_email(email)
    if user_df.empty:
        return jsonify({"success": False, "message": "Email not registered"}), 401

    stored_password = user_df.iloc[0]["password"]
    if not check_password_hash(stored_password, password):
        return jsonify({"success": False, "message": "Incorrect password"}), 401

    return jsonify({"success": True, "message": f"Welcome {user_df.iloc[0]['username']}!"}), 200

@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() if request.is_json else request.form
    username = data.get("username", "").strip()
    new_password = data.get("newPassword", "").strip()

    if not all([username, new_password]):
        return jsonify({"success": False, "message": "Missing username or new password"}), 400

    if not is_strong_password(new_password):
        return jsonify({"success": False, "message": "Password too weak"}), 400

    df = read_users()
    user_index = df[df["username"].str.lower() == username.lower()].index
    if user_index.empty:
        return jsonify({"success": False, "message": "Username not found!"}), 404

    df.at[user_index[0], "password"] = generate_password_hash(new_password)
    save_users(df)

    return jsonify({"success": True, "message": "Password updated successfully!"}), 200

@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() if request.is_json else request.form
    email = data.get("email", "").strip()
    new_password = data.get("newPassword", "").strip()

    if not all([email, new_password]):
        return jsonify({"success": False, "message": "Missing email or new password"}), 400

    if not is_strong_password(new_password):
        return jsonify({"success": False, "message": "Password too weak"}), 400

    df = read_users()
    user_index = df[df["email"].str.lower() == email.lower()].index
    if user_index.empty:
        return jsonify({"success": False, "message": "Email not found!"}), 404

    df.at[user_index[0], "password"] = generate_password_hash(new_password)
    save_users(df)

    return jsonify({"success": True, "message": "Password updated successfully!"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
