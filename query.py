
from fastapi import APIRouter, Form
from vector_store import search_vector_store
from openai import OpenAI
from config import OPENAI_API_KEY
from system_prompt_config import DEFAULT_SYSTEM_PROMPT

router = APIRouter()
client = OpenAI(api_key=OPENAI_API_KEY)

@router.post("/generate_evidence/")
async def generate_evidence(question: str = Form(...), system_prompt: str = Form(None)):
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    retrieved_chunks = search_vector_store(question, 15)
    context = "\n".join(retrieved_chunks)

    prompt = f"""
You are a biomedical research assistant helping interpret cancer genomics studies.

Based only on the context below, extract any relevant numeric breakdowns, classifications, and study design details. Answer in a structured, detailed format.

Context:
{context}

Question: {question}

Answer:"""

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.2,
    )

    return {
        "question": question,
        "answer": completion.choices[0].message.content,
        "chunks": retrieved_chunks
    }
