import os
from langchain_pinecone import PineconeEmbeddings
from pinecone import Pinecone
from config import PINECONE_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("finance-rag")

# Embedding model
embedding_model = PineconeEmbeddings(model='multilingual-e5-large')

def embed_query(query: str) -> list:
    return embedding_model.embed_query(query)


def retrieve_from_namespace(query: str, namespace: str, metadata_filter: dict = None, top_k: int = 10) -> list:
    vec = embed_query(query)
    result = index.query(vector=vec, namespace=namespace, filter=metadata_filter or {}, top_k=top_k, include_metadata=True)
    
    text_chunks = []
    for i, match in enumerate(result.get("matches", []), start=1):
        doc_text = match.get("metadata", {}).get("text", "")
        if doc_text:
            # Prepend each chunk with its index
            text_chunks.append(f"{i}. {doc_text}")

    # Join with newlines to form a numbered list
    return "\n".join(text_chunks)