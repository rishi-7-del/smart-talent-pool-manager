import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

resume = """
Python
Java
SQL
React
Git
Docker
"""

prompt = f"""
Extract only the technical skills.

Return only a comma separated list.

Resume:

{resume}
"""

response = llm.invoke(prompt)

print(response.content)