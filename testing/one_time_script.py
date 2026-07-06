import sqlite3

conn = sqlite3.connect("candidates.db")
cursor = conn.cursor()

cursor.execute("""
SELECT id, name, skills, score, resume_text
FROM candidates
WHERE name='rishi'
""")

print(cursor.fetchone())

conn.close()