import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tools.bootstrap

import chromadb
from typing import cast, Any

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        _client = chromadb.PersistentClient(path='./data/chroma')
        ef = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
        _collection = _client.get_or_create_collection("knowledge_base", embedding_function=cast(Any, ef))
    return _collection

def ingest(docs: list[dict]):
    collection = get_collection()
    ids = [str(doc['id']) for doc in docs]
    texts = [doc['text'] for doc in docs]
    collection.add(documents=texts, ids=ids)

def search_kb(query: str, n=3) -> list[str]:
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=n)
    if results and results.get('documents'):
        docs = results['documents']
        if docs and docs[0] is not None:
            return docs[0]
    return []
