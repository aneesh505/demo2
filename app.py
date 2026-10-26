import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request
from markupsafe import escape

app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24).hex())
app.config["SECRET_KEY"] = SECRET_KEY

DB_PATH = Path(__file__).parent / "users.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("DROP TABLE IF EXISTS users")
    conn.execute("CREATE TABLE users (username TEXT, password TEXT, role TEXT)")
    conn.execute("INSERT INTO users VALUES ('admin', 'admin-pass', 'admin')")
    conn.execute("INSERT INTO users VALUES ('alice', 'alice-pass', 'user')")
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def index():
    return "Demo app is running"

@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    conn = get_db_connection()
    row = conn.execute(query, (username, password)).fetchone()
    conn.close()
    if row:
        return jsonify(status="ok", user=row["username"], role=row["role"])
    return jsonify(status="denied"), 401

@app.get("/hello")
def hello():
    name = request.args.get("name", "world")
    return f"<h1>Hello {escape(name)}</h1>"

if __name__ == "__main__":
    app.run()