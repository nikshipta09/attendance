from flask import Flask, render_template, request, redirect, session
import sqlite3
from collections import defaultdict
from datetime import date

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("school.db")

def setup():
    conn = get_db()

    # Students table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id TEXT PRIMARY KEY,
        name TEXT,
        password TEXT
    )
    """)

    # Attendance table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id TEXT,
        subject TEXT,
        day TEXT,
        status TEXT
    )
    """)

    # Insert sample students (only once)
    conn.execute("INSERT OR IGNORE INTO students VALUES ('101','Swathi','1234')")
    conn.execute("INSERT OR IGNORE INTO students VALUES ('102','Pooja','5678')")

    conn.commit()
    conn.close()

setup()

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        sid = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = get_db()
        cur = conn.execute(
            "SELECT * FROM students WHERE id=? AND password=?",
            (sid, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = sid
            return redirect('/dashboard')
        else:
            return "Invalid ID or Password"

    return render_template("login.html")

# ---------------- ADMIN ----------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        sid = request.form['id']
        name = request.form['name']
        password = request.form['password']

        conn = get_db()
        conn.execute(
            "INSERT OR IGNORE INTO students VALUES (?,?,?)",
            (sid, name, password)
        )
        conn.commit()
        conn.close()

    return render_template("admin.html")

# ---------------- MARK ATTENDANCE ----------------
@app.route('/mark', methods=['POST'])
def mark():
    sid = request.form['id']
    subject = request.form['subject']
    status = request.form['status']
    today = str(date.today())

    conn = get_db()
    conn.execute(
        "INSERT INTO attendance VALUES (?,?,?,?)",
        (sid, subject, today, status)
    )
    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    sid = session['user']
    conn = get_db()

    # Get student name
    cur = conn.execute("SELECT name FROM students WHERE id=?", (sid,))
    row = cur.fetchone()

    if not row:
        return "User not found"

    name = row[0]

    # Get attendance data
    cur = conn.execute(
        "SELECT subject, day, status FROM attendance WHERE id=?",
        (sid,)
    )
    rows = cur.fetchall()

    # -------- AUTO DATA IF EMPTY --------
    if not rows:
        sample = [
            (sid, "Math", "2026-01-01", "Present"),
            (sid, "Science", "2026-01-02", "Present"),
            (sid, "English", "2026-01-03", "Absent"),
            (sid, "History", "2026-01-04", "Present"),
        ]
        conn.executemany("INSERT INTO attendance VALUES (?,?,?,?)", sample)
        conn.commit()

        cur = conn.execute(
            "SELECT subject, day, status FROM attendance WHERE id=?",
            (sid,)
        )
        rows = cur.fetchall()

    conn.close()

    # -------- DATE-WISE --------
    date_data = defaultdict(lambda: {"total": 0, "present": 0})

    for subject, day, status in rows:
        date_data[day]["total"] += 1
        if status == "Present":
            date_data[day]["present"] += 1

    date_labels = sorted(date_data.keys())
    date_percent = [
        (date_data[d]["present"] / date_data[d]["total"]) * 100
        for d in date_labels
    ]

    # -------- MONTHLY --------
    monthly = defaultdict(lambda: {"total": 0, "present": 0})

    for subject, day, status in rows:
        month = day[:7]
        monthly[month]["total"] += 1
        if status == "Present":
            monthly[month]["present"] += 1

    month_labels = list(monthly.keys())
    month_percent = [
        (monthly[m]["present"] / monthly[m]["total"]) * 100
        for m in month_labels
    ]

    # -------- SUBJECT --------
    subjects = defaultdict(lambda: {"total": 0, "present": 0})

    for subject, day, status in rows:
        subjects[subject]["total"] += 1
        if status == "Present":
            subjects[subject]["present"] += 1

    subject_data = {
        s: (v["present"] / v["total"]) * 100
        for s, v in subjects.items()
    }

    return render_template(
        "dashboard.html",
        name=name,
        date_labels=date_labels,
        date_percent=date_percent,
        month_labels=month_labels,
        month_percent=month_percent,
        subject_data=subject_data
    )

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)