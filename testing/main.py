import sqlite3

conn = sqlite3.connect("candidates.db")

cursor = conn.cursor()

MAX_CANDIDATES = 5
weakest_candidate_id = None

cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    skills TEXT,
    score INTEGER
)
""")

conn.commit()

def add_candidate():

    name = input("Enter candidate name: ")

    skills = input("Enter skills: ")

    score = int(input("Enter score: "))

    cursor.execute("SELECT COUNT(*) FROM candidates")

    candidate_count = cursor.fetchone()[0]

    if candidate_count >= MAX_CANDIDATES:

        cursor.execute("""
        SELECT * FROM candidates
        ORDER BY score ASC
        LIMIT 1
        """)

        weakest_candidate = cursor.fetchone()

        weakest_score = weakest_candidate[3]

        if score > weakest_score:

            weakest_candidate_id = weakest_candidate[0]

            cursor.execute(
                "DELETE FROM candidates WHERE id = ?",
                (weakest_candidate_id,)
            )

            print(
                f"Removed weakest candidate: "
                f"{weakest_candidate[1]}"
            )

        else:

            print(
                "Candidate rejected. "
                "Score too low for talent pool."
            )

            return

    cursor.execute(
        "INSERT INTO candidates (name, skills, score) VALUES (?, ?, ?)",
        (name, skills, score)
    )

    conn.commit()

    print("Candidate added successfully.")

def view_candidates():

    cursor.execute("SELECT * FROM candidates")

    candidates = cursor.fetchall()

    print("\nID | Name | Skills | Score")
    print("-" * 50)

    for candidate in candidates:
        print(
            f"{candidate[0]} | "
            f"{candidate[1]} | "
            f"{candidate[2]} | "
            f"{candidate[3]}"
        )

def delete_candidate():

    candidate_name = input(
    "Enter candidate name to delete: "
)

    cursor.execute(
        "DELETE FROM candidates WHERE LOWER(name) = LOWER(?)",
        (candidate_name,)
    )

    conn.commit()

    print("Candidate deleted.")

def rank_candidates():

    cursor.execute(
        "SELECT * FROM candidates ORDER BY score DESC"
    )

    candidates = cursor.fetchall()

    print("\nCANDIDATE RANKINGS")
    print("-" * 50)

    rank = 1

    for candidate in candidates:

        print(
            f"{rank}. "
            f"{candidate[1]} "
            f"- {candidate[3]}"
        )

        rank += 1

def search_candidate():

    search_name = input(
        "Enter candidate name: "
    )

    cursor.execute(
    "SELECT * FROM candidates WHERE LOWER(name) = LOWER(?)",
    (search_name,)
)
    

    candidate = cursor.fetchone()

    if candidate:

        print("\nCandidate Found")

        print(
            f"Name: {candidate[1]}"
        )

        print(
            f"Skills: {candidate[2]}"
        )

        print(
            f"Score: {candidate[3]}"
        )

    else:

        print("Candidate not found.")

def search_by_skill():
    
    skill = input("Enter skill: ")

    cursor.execute(
        "SELECT * FROM candidates WHERE LOWER(skills) LIKE LOWER(?)",
        (f"%{skill}%",)
    )

    candidates = cursor.fetchall()

    if candidates:

        print(f"\nCandidates with skill '{skill}':")
        print("-" * 50)

        for candidate in candidates:
            print(
                f"Name: {candidate[1]}, Score: {candidate[3]}"
            )

    else:

        print(f"No candidates found with skill '{skill}'.")

def filter_by_score():

    minimum_score = int(
        input("Enter minimum score: ")
    )

    cursor.execute(
        """SELECT * FROM candidates
        WHERE score >= ?
        ORDER BY score DESC""",    
          (minimum_score,)
    )

    candidates = cursor.fetchall()

    if candidates:

        print("\nCANDIDATES FOUND")
        print("-" * 50)

        for candidate in candidates:

            print(
                f"{candidate[1]} | "
                f"{candidate[2]} | "
                f"{candidate[3]}"
            )

    else:

        print("No candidates found.")

def statistics_dashboard():

    cursor.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score) FROM candidates")
    average_score = cursor.fetchone()[0]

    cursor.execute("""
    SELECT * FROM candidates
    ORDER BY score DESC
    LIMIT 1
    """)
    top_candidate = cursor.fetchone()

    cursor.execute("""
    SELECT * FROM candidates
    ORDER BY score ASC
    LIMIT 1
    """)
    lowest_candidate = cursor.fetchone()

    print("\nTALENT POOL STATISTICS")
    print("=" * 50)

    print(f"Total Candidates: {total_candidates}")

    if average_score:
        print(f"Average Score: {average_score:.2f}")

    if top_candidate:
        print(
            f"Top Candidate: "
            f"{top_candidate[1]} ({top_candidate[3]})"
        )

    if lowest_candidate:
        print(
            f"Lowest Candidate: "
            f"{lowest_candidate[1]} ({lowest_candidate[3]})"
        )

    print("=" * 50)

while True:

    print("\nSMART TALENT POOL MANAGER")

    print("1. Add Candidate")
    print("2. View Candidates")
    print("3. Delete Candidate")
    print("4. Rank Candidates")
    print("5. Search Candidate")
    print("6. Search by Skill")
    print("7. Filter by Score")
    print("8. Statistics Dashboard")
    print("9. Exit")
    choice = input("Enter choice: ")

    if choice == "1":
        add_candidate()

    elif choice == "2":
        view_candidates()

    elif choice == "3":
        delete_candidate()

    elif choice == "4":
        rank_candidates()

    elif choice == "5":
        search_candidate()

    elif choice == "6":
        search_by_skill()

    elif choice == "7":
        filter_by_score()

    elif choice == "8":
        statistics_dashboard()
    
    elif choice == "9":
        print("Exiting...")
        break

    else:
        print("Invalid Choice")
