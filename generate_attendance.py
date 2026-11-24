import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("school.db")

# Get all students
students = conn.execute("SELECT id FROM students").fetchall()

subjects = ["Math", "Science", "English", "History"]

start_date = datetime(2026, 1, 1)

for student in students:
    sid = student[0]

    # generate 30 days attendance
    for i in range(30):
        day = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

        for subject in subjects:
            status = random.choice(["Present", "Absent"])

            conn.execute(
                "INSERT INTO attendance VALUES (?,?,?,?)",
                (sid, subject, day, status)
            )

conn.commit()
conn.close()

print("✅ Unique attendance generated for all students!")