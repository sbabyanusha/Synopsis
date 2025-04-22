
import os
import numpy as np
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma

VECTORSTORE_DIR = "./vector_store"
collection_name = "pdf_chunks"

llm = ChatOllama(model="mistral")

# 👇 Mock embedding class to bypass Ollama embedding
class MockEmbeddings:
    def embed_query(self, text):
        print(f"⚠️ Mock embedding used for query: '{text[:30]}...'")
        return np.random.rand(768).tolist()

    def embed_documents(self, texts):
        print(f"⚠️ Mock embedding used for {len(texts)} documents.")
        return [np.random.rand(768).tolist() for _ in texts]

embeddings_model = MockEmbeddings()

vector_store = Chroma(
    collection_name=collection_name,
    embedding_function=embeddings_model,
    persist_directory=VECTORSTORE_DIR
)

def add_embeddings(chunks):
    print("🔢 Starting mock embedding process...")
    texts = [chunk.page_content for chunk in chunks]
    metadata = [{"source": chunk.metadata.get("source", "")} for chunk in chunks]

    try:
        vector_store.add_texts(texts=texts, metadata=metadata)
        print(f"✅ Mock added {len(texts)} chunks to vector store")
    except Exception as e:
        print("❌ Failed to add embeddings:", e)

    return len(texts)

def search_vector_store(question, k=5):
    try:
        print(f"🔍 Embedding query with mock: {question}")
        query_embedding = embeddings_model.embed_query(question)
        results = vector_store.similarity_search_by_vector(query_embedding, k=k)
        print(f"🔎 Retrieved {len(results)} results from vector store")
        return [doc.page_content for doc in results]
    except Exception as e:
        print("❌ Vector store query failed:", e)
        return []

def clear_vector_store():
    global vector_store
    print("🧹 Clearing vector store...")
    vector_store.delete_collection()
    del vector_store
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings_model,
        persist_directory=VECTORSTORE_DIR
    )
    print("✅ Vector store cleared.")
