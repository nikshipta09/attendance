import sqlite3
import csv

conn = sqlite3.connect("school.db")

with open("students.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)  # skip header

    for row in reader:
        sid = row[0]
        name = row[1]

        # default password = student ID
        password = sid

        conn.execute(
            "INSERT OR IGNORE INTO students (id, name, password) VALUES (?, ?, ?)",
            (sid, name, password)
        )

conn.commit()
conn.close()

print("Students imported successfully!")