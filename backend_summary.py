
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import pandas as pd
from openai import OpenAI
from pdf_ingest import process_pdf
from system_prompt_config import DEFAULT_SYSTEM_PROMPT

app = FastAPI()
client = OpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/summarize_pdf/")
async def summarize_pdf(file: UploadFile = File(...)):
    # Save PDF to disk temporarily
    pdf_path = f"temp_{file.filename}"
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Process PDF to extract chunks
    chunks = process_pdf(pdf_path)
    os.remove(pdf_path)

    if not chunks:
        raise HTTPException(status_code=400, detail="No text found in the PDF.")

    # Join chunks into a single context
    context = "\n".join(doc.page_content for doc in chunks[:15])


    prompt = f"{DEFAULT_SYSTEM_PROMPT}\n\nContext:\n{context}\n\nPlease summarize the above document."

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3,
        )
        return {"summary": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
