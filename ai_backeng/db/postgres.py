import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está definida")

_pool: asyncpg.Pool | None = None


async def init_db():
    """
    Inicializa el pool de conexiones.
    Se llama UNA sola vez al arrancar FastAPI.
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10
        )


async def get_pool() -> asyncpg.Pool:
    """
    Devuelve el pool ya inicializado.
    """
    if _pool is None:
        raise RuntimeError("DB no inicializada. Llama init_db() primero.")
    return _pool

