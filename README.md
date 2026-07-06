# Smart Talent Pool Manager

An AI-powered recruitment application that processes PDF resumes, extracts technical skills, and performs semantic candidate search using vector embeddings.

## Overview

The Smart Talent Pool Manager helps recruiters organize and search a candidate pool more intelligently.

Instead of relying only on exact keyword matching, the application uses AI-extracted technical skills, vector embeddings, and semantic similarity search to rank candidates based on the meaning of a recruiter's query.

## Features

- Upload candidate resumes in PDF format
- Extract resume text automatically
- Extract technical skills using Google Gemini
- Store structured candidate data using SQLite
- Generate semantic embeddings from extracted skills
- Store and search vectors using Qdrant
- Search candidates by role, skill, or technology
- Display AI Match percentages
- View original uploaded resumes
- Track recruiter evaluation scores
- Display pending evaluations clearly
- Manage a fixed-size talent pool

## How It Works

1. A recruiter uploads a candidate's PDF resume.
2. PyPDF2 extracts the text from the PDF.
3. Google Gemini extracts only the candidate's technical skills.
4. The extracted skills are converted into a vector embedding.
5. Qdrant stores the candidate vector.
6. A recruiter enters a search query such as `Backend Developer`.
7. The query is also converted into an embedding.
8. Qdrant finds the most semantically similar candidates.
9. The application displays candidates ranked by AI Match percentage.

## Architecture

```text
PDF Resume
    ↓
PyPDF2 Text Extraction
    ↓
Gemini Skill Extraction
    ↓
Technical Skills
    ↓
Gemini Embeddings
    ↓
Qdrant Vector Search
    ↓
Candidate Ranking
    ↓
Flask Web Interface