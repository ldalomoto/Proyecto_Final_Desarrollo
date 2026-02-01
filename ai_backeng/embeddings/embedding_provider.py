import os
from dotenv import load_dotenv
import voyageai

# Cargar variables desde .env
load_dotenv()

# Configuración
PROVIDER = os.getenv("EMBEDDING_PROVIDER", "voyage")

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
if not VOYAGE_API_KEY:
    raise RuntimeError("VOYAGE_API_KEY not set in .env")

voyageai.api_key = VOYAGE_API_KEY

EMBEDDING_MODEL_NAME = "voyage-4-lite"

client = voyageai.Client()

def get_embedding(text: str) -> list[float]:
    if PROVIDER != "voyage":
        raise RuntimeError("Embedding provider not supported")

    response = client.embed(
        texts=[text],
        model=EMBEDDING_MODEL_NAME
    )

    return response.embeddings[0]
