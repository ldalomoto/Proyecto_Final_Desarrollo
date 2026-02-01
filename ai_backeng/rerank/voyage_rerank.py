import os
import requests

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
VOYAGE_RERANK_URL = "https://api.voyageai.com/v1/rerank"

def rerank_careers(
    user_query: str,
    careers: list[dict],
    top_k: int = 5
):
    if not careers:
        return []

    documents = [
        f"Carrera: {c['career_name']}. "
        f"Modalidad: {c['modality']}. "
        f"Duración: {c['duration']} semestres. "
        f"Descripción: {c.get('description', '')[:150]}"
        for c in careers
    ]

    payload = {
        "model": "rerank-2.5-lite",
        "query": user_query,
        "documents": documents,
        "top_k": top_k
    }

    headers = {
        "Authorization": f"Bearer {VOYAGE_API_KEY}",
        "Content-Type": "application/json"
    }

    res = requests.post(
        VOYAGE_RERANK_URL,
        json=payload,
        headers=headers,
        timeout=20
    )

    res.raise_for_status()
    data = res.json()["data"]

    return [careers[item["index"]] for item in data]
