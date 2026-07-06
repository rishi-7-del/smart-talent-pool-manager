import sqlite3

conn = sqlite3.connect("candidates.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE candidates
ADD COLUMN resume_text TEXT
""")

conn.commit()
conn.close()

print("Database updated successfully!")