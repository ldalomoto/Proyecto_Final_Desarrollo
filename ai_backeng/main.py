from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware  # <--- IMPORTANTE
from pydantic import BaseModel
from ai_backeng.db.postgres import init_db, get_pool
from ai_backeng.embeddings.embedding_provider import get_embedding
from ai_backeng.embeddings.blend import blend_embeddings
from ai_backeng.matching.get_best_careers import get_best_careers
from ai_backeng.agent import run_agent
from ai_backeng.memory.redis_manager import SessionManager
from ai_backeng.memory.extractor import extract_profile_updates
from datetime import datetime, timezone
from ai_backeng.memory.tiempo import should_greet_user
from fastapi.responses import StreamingResponse
from ai_backeng.agent import run_agent_stream
from ai_backeng.agent import build_user_embedding_text

def now():
    return datetime.now(timezone.utc)

app = FastAPI()

# =========================
# CONFIGURACIÓN CORS (EL PUENTE)
# =========================
origins = [
    "http://localhost:5173",                 # Para cuando pruebas en tu PC
    "https://unidream.vercel.app",           # Tu frontend en producción
    "https://unidream-git-main-francocriollos-projects.vercel.app" # Preview deployments (opcional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],    # Permitir GET, POST, OPTIONS, etc.
    allow_headers=["*"],    # Permitir enviar JSON, Tokens, etc.
)
session_manager = SessionManager()

class ChatInput(BaseModel):
    user_id: str  # Ahora identificamos al usuario
    message: str

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/reset-session")
async def reset_session(user_id: str):
    session_manager.delete(user_id)
    return {"status": "ok"}

@app.post("/chat")
async def chat(input: ChatInput):
    pool = await get_pool()

    # 1. Recuperamos memoria de Redis
    user_memory = session_manager.get_profile(input.user_id)
    meta = user_memory.setdefault("meta", {})

    # 2. Decidimos saludo ANTES de tocar timestamps
    should_greet = should_greet_user(meta)
    if should_greet:
        meta["last_greeted_at"] = now().isoformat()

    # 3. Extractor
    extraction_result = extract_profile_updates(input.message, user_memory)
    profile_update = extraction_result["profile_data"]
    should_update_embedding = extraction_result["has_career_intent"]

    # 4. Fusionamos memoria existente con lo nuevo
    # Nombre
    if profile_update.get("nombre"):
        user_memory["nombre"] = profile_update["nombre"]

    # Preferencias
    for key, value in profile_update.get("preferencias", {}).items():
        if value:
            user_memory.setdefault("preferencias", {})[key] = value

    # Habilidades percibidas
    if profile_update.get("habilidades_percibidas"):
        user_memory["habilidades_percibidas"] = list(
            set(user_memory.get("habilidades_percibidas", []) +
                profile_update.get("habilidades_percibidas", []))
        )

    # Materias fuertes
    if profile_update.get("materias_fuertes"):
        user_memory["materias_fuertes"] = list(
            set(user_memory.get("materias_fuertes", []) +
                profile_update.get("materias_fuertes", []))
        )

    # Materias débiles
    if profile_update.get("materias_debiles"):
        user_memory["materias_debiles"] = list(
            set(user_memory.get("materias_debiles", []) +
                profile_update.get("materias_debiles", []))
        )

        # Limpiar intereses que el usuario no quiere
        for materia in profile_update.get("materias_debiles", []):
            if materia in user_memory.get("intereses", []):
                user_memory["intereses"].remove(materia)

    # Intereses
    if profile_update.get("intereses"):
        user_memory["intereses"] = list(
            set(user_memory.get("intereses", []) +
                profile_update.get("intereses", []))
        )

    # 5. Actualizamos meta
    meta["last_seen_at"] = now().isoformat()
    meta["message_count"] = meta.get("message_count", 0) + 1

    # 6. Embeddings
    if should_update_embedding:
        profile_text = build_user_embedding_text(user_memory)
        new_emb = get_embedding(profile_text)
        current_emb = user_memory.get("user_embedding")
        user_memory["user_embedding"] = (
            blend_embeddings(current_emb, new_emb) if current_emb else new_emb
        )

    # 7. Matching de carreras
    careers = []
    if user_memory.get("user_embedding"):
        careers = await get_best_careers(
            pool,
            user_memory["user_embedding"],
            user_memory.get("preferencias", {})
        )

    # 8. Respuesta del agente
    reply = run_agent(
        input.message,
        user_memory,
        careers,
        should_greet=should_greet
    )

    # 9. Persistimos sesión (ya guardamos saludo arriba)
    session_manager.save_profile(input.user_id, user_memory)

    return {"reply": reply}

@app.post("/chat/stream")
async def chat_stream(input: ChatInput):
    pool = await get_pool()

    # 1. Recuperamos memoria
    user_memory = session_manager.get_profile(input.user_id)
    meta = user_memory.setdefault("meta", {})

    # 2. Decidimos saludo ANTES de tocar timestamps
    should_greet = should_greet_user(meta)
    if should_greet:
        meta["last_greeted_at"] = now().isoformat()  # Guardamos inmediatamente

    # 3. Extractor
    extraction_result = extract_profile_updates(input.message, user_memory)
    profile_update = extraction_result["profile_data"]
    should_update_embedding = extraction_result["has_career_intent"]

    # 4. Fusionamos memoria existente con lo nuevo

    # Nombre
    if profile_update.get("nombre"):
        user_memory["nombre"] = profile_update["nombre"]

    # Preferencias (aceptamos False)
    for key, value in profile_update.get("preferencias", {}).items():
        if value is not None:
            user_memory.setdefault("preferencias", {})[key] = value

    # Habilidades percibidas
    if profile_update.get("habilidades_percibidas"):
        user_memory["habilidades_percibidas"] = list(
            set(user_memory.get("habilidades_percibidas", []) +
                profile_update.get("habilidades_percibidas", []))
        )

    # Materias fuertes
    if profile_update.get("materias_fuertes"):
        user_memory["materias_fuertes"] = list(
            set(user_memory.get("materias_fuertes", []) +
                profile_update.get("materias_fuertes", []))
        )

    # Materias débiles
    if profile_update.get("materias_debiles"):
        user_memory["materias_debiles"] = list(
            set(user_memory.get("materias_debiles", []) +
                profile_update.get("materias_debiles", []))
        )
        # Limpiar intereses que el usuario no quiere
        for materia in profile_update.get("materias_debiles", []):
            if materia in user_memory.get("intereses", []):
                user_memory["intereses"].remove(materia)

    # Intereses
    if profile_update.get("intereses"):
        user_memory["intereses"] = list(
            set(user_memory.get("intereses", []) +
                profile_update.get("intereses", []))
        )

    # 5. Actualizamos meta
    meta["last_seen_at"] = now().isoformat()
    meta["message_count"] = meta.get("message_count", 0) + 1

    # 6. Embeddings
    if should_update_embedding:
        profile_text = build_user_embedding_text(user_memory)
        new_emb = get_embedding(profile_text)
        current_emb = user_memory.get("user_embedding")
        user_memory["user_embedding"] = (
            blend_embeddings(current_emb, new_emb) if current_emb else new_emb
        )

    # 7. Matching de carreras
    careers = []
    if user_memory.get("user_embedding"):
        careers = await get_best_careers(
            pool,
            user_memory["user_embedding"],
            user_memory.get("preferencias", {})
        )

    def generator():
        has_content = False

        # 1️⃣ Iteramos los chunks del modelo
        for chunk in run_agent_stream(input.message, user_memory, careers, should_greet):
            for candidate in chunk.candidates:
                for part in candidate.content.parts:
                    if part.text.strip():   # ignoramos strings vacíos
                        has_content = True
                        yield part.text

        # 2️⃣ Fallback si no hubo contenido
        if not has_content:
            yield "Lo siento, no pude generar una respuesta en este momento.\n"

        # 3️⃣ Guardamos la memoria del usuario **al final del streaming**
        session_manager.save_profile(input.user_id, user_memory)

        # 4️⃣ Marcamos fin de la transmisión
        yield "\n[END]\n"

    return StreamingResponse(
        generator(),
        media_type="text/plain"
    )
