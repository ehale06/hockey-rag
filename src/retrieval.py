import json
import os
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

COLLECTION_NAME = "hockey_rag"
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None
_collection = None

def load_processed_documents() -> list:
    with open(Path("data") / "processed_documents.json", "r") as f:
        return json.load(f)

def build_vector_store():
    print("Loading documents...")
    documents = load_processed_documents()

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=".chroma")

    try:
        client.delete_collection(COLLECTION_NAME)
        print("Deleted existing collection")
    except:
        pass

    collection = client.create_collection(COLLECTION_NAME)

    print(f"Embedding and storing {len(documents)} documents...")
    texts = [doc["text"] for doc in documents]
    metadatas = [{
        "source": doc.get("source", ""),
        "type": doc.get("type", ""),
        "team": doc.get("team", ""),
        "player": doc.get("player", "")
    } for doc in documents]
    ids = [f"doc_{i}" for i in range(len(documents))]

    embeddings = model.encode(texts, show_progress_bar=True)

    collection.add(
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
        ids=ids
    )

    print(f"\nVector store built successfully.")
    print(f"Total documents stored: {collection.count()}")
    return collection

def get_retriever():
    global _model, _collection
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
    if _collection is None:
        client = chromadb.PersistentClient(path=".chroma")
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection, _model

def detect_query_intent(query: str) -> str:
    query_lower = query.lower()

    if any(phrase in query_lower for phrase in [
        "olympic break", "olympics", "since olympics",
        "all-star break", "all star break",
        "since february", "last month", "recently", "lately",
        "past few games", "last few games"
    ]):
        return "post_olympic"

    if any(phrase in query_lower for phrase in [
        "last 10", "last ten", "recent games", "last games",
        "past 10", "past ten", "recent form"
    ]):
        return "last_10"

    if any(phrase in query_lower for phrase in [
        "how are the", "how is the team", "standings",
        "playoff", "division", "conference", "record"
    ]):
        return "team_performance"

    if any(phrase in query_lower for phrase in [
        "how many points", "how many goals", "how many assists",
        "season stats", "this season", "season total",
        "points does", "goals does", "assists does",
        "stats for", "how is", "how has", "performing"
    ]):
        return "season_summary"

    if any(phrase in query_lower for phrase in [
        "top scorers", "leading scorer", "most points",
        "best players", "top players"
    ]):
        return "scoring_summary"

    return "general"

def retrieve(query: str, n_results: int = 5) -> list:
    collection, model = get_retriever()
    intent = detect_query_intent(query)
    query_embedding = model.encode([query]).tolist()

    if intent == "post_olympic":
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"type": "post_olympic_summary"}
        )
        docs = results["documents"][0]
        if docs:
            return docs

    if intent == "last_10":
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"type": "last_10_games"}
        )
        docs = results["documents"][0]
        if docs:
            return docs

    if intent == "team_performance":
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"type": "standings"}
        )
        docs = results["documents"][0]
        if docs:
            return docs

    if intent == "season_summary":
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"type": {"$in": ["season_summary", "player_stats"]}}
        )
        docs = results["documents"][0]
        if docs:
            return docs

    if intent == "scoring_summary":
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"type": "scoring_summary"}
        )
        docs = results["documents"][0]
        if docs:
            return docs

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results["documents"][0]

if __name__ == "__main__":
    build_vector_store()