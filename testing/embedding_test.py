import os

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=api_key
)

from sklearn.metrics.pairwise import cosine_similarity

text1 = "Python, Flask, SQL"
text2 = "Backend Developer"
text3 = "Graphic Designer"

vector1 = embeddings.embed_query(text1)
vector2 = embeddings.embed_query(text2)
vector3 = embeddings.embed_query(text3)

similarity1 = cosine_similarity([vector1], [vector2])[0][0]
similarity2 = cosine_similarity([vector1], [vector3])[0][0]

print()

print(f"{text1}")
print(f"{text2}")
print(f"Similarity: {similarity1:.4f}")

print()

print(f"{text1}")
print(f"{text3}")
print(f"Similarity: {similarity2:.4f}")