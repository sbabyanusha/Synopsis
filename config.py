import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store")
PUBLICATIONS_DIR = "publications"