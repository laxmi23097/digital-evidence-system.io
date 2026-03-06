from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib
from datetime import datetime
import webbrowser
import threading

app = Flask(__name__)

def connect_db():
    return sqlite3.connect("database.db")

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT,
        hash_value TEXT,
        uploaded_by TEXT,
        upload_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custody_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_id INTEGER,
        action TEXT,
        handled_by TEXT,
        date_time TEXT
    )
    """)

    conn.commit()
    conn.close()

create_tables()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name=? AND password=?", (username,password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users(name,password) VALUES(?,?)",(username,password))
            conn.commit()
            conn.close()
            return redirect("/")
        except:
            return render_template("register.html", error="Username already exists")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        filename = file.filename
        file_data = file.read()
        hash_value = hashlib.sha256(file_data).hexdigest()
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO evidence(file_name,hash_value,uploaded_by,upload_date)
        VALUES(?,?,?,?)
        """,(filename,hash_value,"admin",upload_time))

        evidence_id = cursor.lastrowid
        cursor.execute("""
        INSERT INTO custody_log(evidence_id,action,handled_by,date_time)
        VALUES(?,?,?,?)
        """,(evidence_id,"Uploaded","admin",upload_time))

        conn.commit()
        conn.close()
        return render_template("upload.html", success="Evidence Uploaded Successfully")

    return render_template("upload.html")

@app.route("/evidence")
def evidence():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evidence")
    data = cursor.fetchall()
    conn.close()
    return render_template("evidence.html", records=data)

@app.route("/custody")
def custody():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM custody_log")
    logs = cursor.fetchall()
    conn.close()
    return render_template("custody.html", logs=logs)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.25, open_browser).start()  # opens browser automatically
    app.run(debug=True)