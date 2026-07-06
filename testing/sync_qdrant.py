import os
import sqlite3

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from qdrant_client import QdrantClient

from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

conn = sqlite3.connect("candidates.db")

cursor = conn.cursor()

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=api_key
)

client = QdrantClient(":memory:")

client.create_collection(

    collection_name="candidates",

    vectors_config=VectorParams(

        size=3072,

        distance=Distance.COSINE

    )

)

cursor.execute(
    "SELECT * FROM candidates"
)

candidates = cursor.fetchall()

for candidate in candidates:

    candidate_id = candidate[0]

    name = candidate[1]

    skills = candidate[2]

    score = candidate[3]

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

                "score": score

            }

        )

    ]

)
    
results = client.scroll(

    collection_name="candidates",

    limit=10

)

print(results)

query = "Backend Python Developer"

query_vector = embeddings.embed_query(query)

search_results = client.query_points(

    collection_name="candidates",

    query=query_vector,

    limit=3

)

print()

print("Top Matches:")

for result in search_results.points:

    print(result.payload)

    print(result.score)

    print("----------------")