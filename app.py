from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"
# Test commit
def connect_db():
    return sqlite3.connect("database.db")
conn = connect_db()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS complaints(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    category TEXT,
    description TEXT,
    priority TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

conn.commit()
conn.close()

@app.route('/')
def home():
    return """
    <h1>Complaint Management System</h1>
    <p>Project is running successfully.</p>
    <a href='/login'>Login</a>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['name'] = user[1]

            return redirect('/dashboard')

        return "Invalid Email or Password"

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (name, email, password)
            )
            conn.commit()

        except:
            return "Email already exists"

        conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
    'dashboard.html',
    name=session['name']
)
    
    
@app.route('/my_complaints')
def my_complaints():

    if 'user_id' not in session:
        return redirect('/login')

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, status FROM complaints WHERE user_id=?",
        (session['user_id'],)
    )

    complaints = cursor.fetchall()

    conn.close()

    return render_template(
        'my_complaints.html',
        complaints=complaints
    )    
    
    
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')    

@app.route('/complaint', methods=['GET', 'POST'])
def complaint():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO complaints(user_id, title, description) VALUES(?,?,?)",
            (session['user_id'], title, description)
        )

        conn.commit()
        conn.close()

        return "Complaint Submitted Successfully"

    return render_template('complaint.html')

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )