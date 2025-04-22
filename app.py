
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gene_extract import router as gene_router
from query import router as query_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gene_router)
app.include_router(query_router)
