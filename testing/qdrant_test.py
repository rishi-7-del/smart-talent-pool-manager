import os

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from qdrant_client import QdrantClient

from qdrant_client.models import VectorParams, Distance, PointStruct

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

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

print(client.get_collections())

text = "Python, Flask, SQL"

vector = embeddings.embed_query(text)

client.upsert(

    collection_name="candidates",

    points=[

        PointStruct(

            id=1,

            vector=vector,

            payload={

                "name": "Mike",

                "skills": "Python, Flask, SQL"

            }

        )

    ]

)

results = client.scroll(
    collection_name="candidates",
    limit=10
)

print(results)