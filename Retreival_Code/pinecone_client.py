import re
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

def retrieve_academic_text():
    rep_ids = ['4752ea92-b939-4c4a-87ed-029a739bfd6e', 'ead42f02-30ef-4c62-af74-6dfce7174b98', '497e6d4c-6e5e-4c94-b2f1-a7cd618f9294', 'cab4d6c4-b119-428e-a1f7-e9a615132fec', '94ffc23e-1f7b-4370-a0aa-a454df2d6242', '7dee1033-cb84-42dd-8897-2e2630e9fd22', '059fbc18-5a3e-4391-83e5-3bc8312882f6', '76bcef74-4fd4-4318-aef5-4d0073460a1d', '411ca021-6d59-4f14-a3cd-70d2fa6cd8c9', '271bff4f-f51f-45c1-b673-09c649d32e93']
    reps = index.fetch(ids=rep_ids, namespace="academic-papers").vectors
    reps_text = [reps[rid].metadata['text'] for rid in rep_ids]
    return "\n".join(reps_text)

def retrieve_academic_text_query():
    queries = [
        "Tobin’s q definition firm value ratio replacement cost theoretical concept",
        "Tobin’s q theoretical properties investment sensitivity adjustment dynamics",
        "Tobin’s q empirical regularities cross-sectional studies average median skewness",
        "marginal Tobin’s q distribution firm-level histogram kurtosis outliers",
    ]

    texts = []
    for query in queries:
        raw = retrieve_from_namespace(
            query=query,
            namespace="academic-papers",
            top_k=5
        )
        # 1) remove null bytes
        clean = raw.replace('\x00', '')
        # 2) optionally remove any other weird control chars (e.g., ASCII <32 except newline/tab)
        clean = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', clean)
        texts.append(clean)

    result = "\n".join(texts)

    # also save in a txt file
    with open("academic_text.txt", "w", encoding="utf-8") as f:
        f.write(result)

    return result