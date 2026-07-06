from flask import Flask, render_template, request, redirect, flash
import sqlite3

from werkzeug.utils import secure_filename
from flask import send_from_directory

from langchain_google_genai import ChatGoogleGenerativeAI

import os

import PyPDF2

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from qdrant_client import QdrantClient

from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

app = Flask(__name__)
app.secret_key = "smart_talent_pool"
MAX_CANDIDATES = 5

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=api_key
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0
)

client = QdrantClient(":memory:")

client.create_collection(
    collection_name="candidates",

    vectors_config=VectorParams(
        size=3072,
        distance=Distance.COSINE
    )
)

def sync_database():

    client.recreate_collection(

        collection_name="candidates",

        vectors_config=VectorParams(
            size=3072,
            distance=Distance.COSINE
        )
    )

    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidates")

    candidates = cursor.fetchall()

    for candidate in candidates:

        candidate_id = candidate[0]

        name = candidate[1]

        skills = candidate[2]
        
        score = candidate[3]

        resume_text = candidate[4]
        
        vector = embeddings.embed_query(skills)
        
        client.upsert(

            collection_name="candidates",

            points=[

                PointStruct(

                    id=candidate_id,

                    vector=vector,

                    payload={
                        "name": name,
                        "skills": skills,
                        "resume_text": resume_text,
                        "score": score
                    }

                )

            ]

        )

    conn.close()

sync_database()

@app.route("/")
def home():

    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()

    search = request.args.get("search", "")

    match_scores = {}

    if search:

        query_vector = embeddings.embed_query(search)

        search_results = client.query_points(

        collection_name="candidates",

        query=query_vector,

        limit=10
        )

        for result in search_results.points:

            match_scores[result.id] = round(result.score * 100, 1)

        candidate_ids = []

        for result in search_results.points:
            candidate_ids.append(result.id)

        if candidate_ids:

            placeholders = ",".join(["?"] * len(candidate_ids))

            cursor.execute(
                f"""
                SELECT *
                FROM candidates
                WHERE id IN ({placeholders})
                """,
                candidate_ids
            )

            candidates = cursor.fetchall()

            id_order = {candidate_id: index for index, candidate_id in enumerate(candidate_ids)}
            candidates.sort(key=lambda candidate: id_order[candidate[0]])

        else:

            candidates = []

    else:

        cursor.execute(
        "SELECT * FROM candidates"
    )

        candidates = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score) FROM candidates")
    average_score = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(score) FROM candidates")
    highest_score = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(score) FROM candidates")
    lowest_score = cursor.fetchone()[0]

    conn.close()

    return render_template(
    "index.html",
    candidates=candidates,
    search=search,
    total_candidates=total_candidates,
    average_score=average_score,
    highest_score=highest_score,
    lowest_score=lowest_score,
    match_scores=match_scores
)

@app.route("/add", methods=["POST"])
def add_candidate():

    name = request.form["name"]
    resume = request.files.get("resume")

    resume_filename = None

    if resume and resume.filename:

        resume_filename = secure_filename(resume.filename)

        resume.save(
            os.path.join("uploads", resume_filename)
        )

    if resume and resume.filename:

        pdf_reader = PyPDF2.PdfReader(resume)

        extracted_text = ""

        for page in pdf_reader.pages:

            text = page.extract_text()

            if text:
                extracted_text += text

        prompt = f"""
        Extract only technical skills from this resume.

        Rules:
        - Include programming languages.
        - Include frameworks.
        - Include databases.
        - Include cloud platforms.
        - Include developer tools.
        - Include libraries.
        - Include technologies.
        - Do not include education.
        - Do not include projects.
        - Do not include certifications.
        - Do not include soft skills.
        - Do not include phone numbers.
        - Do not include email addresses.
        - Do not include CGPA.
        - Return only one comma-separated line.
        - Do not explain anything.

        Resume:

        {extracted_text}
        """

        response = llm.invoke(prompt)

        skills = response.content.strip()

        resume_text = extracted_text

        score = 0
    else:

        flash(
            "Please upload a PDF resume.",
            "danger"
        )

        return redirect("/") 
    
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM candidates")
    candidate_count = cursor.fetchone()[0]

    # Pool is not full
    if candidate_count < MAX_CANDIDATES:

        cursor.execute(
            """
            INSERT INTO candidates
            (name, skills, resume_text, score,resume_file)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, skills, resume_text, score, resume_filename)
        )

        conn.commit()
        sync_database()
        flash(
            f"{name} was added successfully!",
            "success"
        )
        conn.close()
        
        return redirect("/")

    # Pool is full
    cursor.execute("""
    SELECT *
    FROM candidates
    ORDER BY score ASC
    LIMIT 1
    """)

    weakest_candidate = cursor.fetchone()

    weakest_candidate_id = weakest_candidate[0]
    weakest_candidate_score = weakest_candidate[3]

    # New candidate is better
    if score > weakest_candidate_score:

        cursor.execute(
            "DELETE FROM candidates WHERE id = ?",
            (weakest_candidate_id,)
        )

        cursor.execute(
            """
            INSERT INTO candidates
            (name, skills, resume_text, score, resume_file)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, skills, resume_text, score, resume_filename)
        )

        conn.commit()
        sync_database()

        flash(
            f"Talent pool was full. "
            f"{name} replaced "
            f"{weakest_candidate[1]} "
            f"(Score: {weakest_candidate_score}).",
            "warning"
        )

    else:

        flash(
            f"Talent pool is full. "
            f"{name} was rejected because their score "
            f"({score}) is lower than the weakest "
            f"candidate's score ({weakest_candidate_score}).",
            "danger"
        )

    conn.close()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete_candidate(id):

    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM candidates WHERE id = ?",
        (id,)
    )

    conn.commit()
    sync_database()
    conn.close()

    return redirect("/")

@app.route("/resume/<filename>")
def view_resume(filename):

    return send_from_directory(
        "uploads",
        filename
    )

if __name__ == "__main__":
    app.run(debug=True)