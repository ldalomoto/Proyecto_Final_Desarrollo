from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime, timezone
from ai_backeng.db.postgres import init_db, get_pool
from ai_backeng.embeddings.embedding_provider import get_embedding
from ai_backeng.embeddings.blend import blend_embeddings
from ai_backeng.matching.get_best_careers import get_best_careers
from ai_backeng.agent import run_agent, run_agent_stream, build_user_embedding_text
from ai_backeng.memory.redis_manager import SessionManager
from ai_backeng.memory.extractor import extract_profile_updates
from ai_backeng.memory.tiempo import should_greet_user
from ai_backeng.routers import careers
from uuid import UUID


def now():
    return datetime.now(timezone.utc)

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def normalize_for_json(obj):
    if isinstance(obj, dict):
        return {k: normalize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_for_json(v) for v in obj]
    if isinstance(obj, UUID):
        return str(obj)
    return obj


app = FastAPI()

# =========================
# CONFIGURACIÓN CORS (EL PUENTE)
# =========================
origins = [
    "http://localhost:5173",
    "http://3.21.97.112:5173",   # 👈 ESTA ES LA CLAVE
    "https://unidream.vercel.app",
    "https://unidream-git-main-francocriollos-projects.vercel.app",
]

#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=origins,
#    allow_credentials=True,
#    allow_methods=["*"],    # Permitir GET, POST, OPTIONS, etc.
#    allow_headers=["*"],    # Permitir enviar JSON, Tokens, etc.
#)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://3.21.97.112:5173",
        "https://unidream.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionManager()

class ChatInput(BaseModel):
    user_id: str  # Ahora identificamos al usuario
    message: str

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(careers.router)

@app.post("/reset-session")
async def reset_session(user_id: str):
    session_manager.delete(user_id)
    return {"status": "ok"}

@app.get("/users/{user_id}/recommendations")
def get_user_recommendations(user_id: str):
    user_memory = session_manager.get_profile(user_id)

    recommendations = user_memory.get("recomendaciones", [])

    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

@app.get("/users/{user_id}/recommendations/full")
async def get_user_recommendations_full(user_id: str):
    pool = await get_pool()
    user_memory = session_manager.get_profile(user_id)
    recs = user_memory.get("recomendaciones", [])

    if not recs:
        return {"recommendations": []}

    career_ids = [r["career_id"] for r in recs if r.get("career_id")]

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                c.id AS career_id,
                c.career_name,
                c.description,
                c.modality,
                c.duration,
                u.name AS university_name
            FROM careers c
            JOIN universities u ON u.id = c.university_id
            WHERE c.id = ANY($1::uuid[])
        """, career_ids)

    career_map = {str(r["career_id"]): dict(r) for r in rows}

    enriched = []
    for r in recs:
        base = career_map.get(str(r["career_id"]), {})
        enriched.append({
            **base,
            "score": r["score"],
            "timestamp": r["timestamp"]
        })

    return {"recommendations": enriched}


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
    # 7. Matching de carreras
    careers = []

    if user_memory.get("user_embedding"):
        enriched_preferences = {
            **user_memory.get("preferencias", {}),
            "intereses": user_memory.get("intereses", []),
            "habilidades_percibidas": user_memory.get("habilidades_percibidas", []),
            "materias_fuertes": user_memory.get("materias_fuertes", [])
        }

        careers = await get_best_careers(
            pool,
            user_memory["user_embedding"],
            enriched_preferences
        )

        # 7.1 Guardar recomendaciones en Redis
        if careers:
            user_memory.setdefault("recomendaciones", [])

            for c in careers:
                rec = {
                    "career_id": c.get("career_id"),
                    "career_name": c.get("career_name"),
                    "university_id": c.get("university_id"),
                    "university_name": c.get("university_name"),
                    "timestamp": now_iso(),
                    "context": input.message,
                    "score": c.get("score")
                }

                if not any(
                    r.get("career_id") == rec["career_id"]
                    for r in user_memory["recomendaciones"]
                    if r.get("career_id") is not None
                ):
                    user_memory["recomendaciones"].append(rec)



    print("Rerank query context:", enriched_preferences)




    # 8. Respuesta del agente
    reply = run_agent(
        input.message,
        user_memory,
        careers,
        should_greet=should_greet
    )

    # 9. Persistimos sesión (ya guardamos saludo arriba)
    user_memory = normalize_for_json(user_memory)
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
        enriched_preferences = {
            **user_memory.get("preferencias", {}),
            "intereses": user_memory.get("intereses", []),
            "habilidades_percibidas": user_memory.get("habilidades_percibidas", []),
            "materias_fuertes": user_memory.get("materias_fuertes", [])
        }

        careers = await get_best_careers(
            pool,
            user_memory["user_embedding"],
            enriched_preferences
        )

        # 7.1 Guardar recomendaciones en Redis
        if careers:
            user_memory.setdefault("recomendaciones", [])

            for c in careers:
                rec = {
                    "career_id": c.get("career_id"),
                    "career_name": c.get("career_name"),
                    "university_id": c.get("university_id"),
                    "university_name": c.get("university_name"),
                    "timestamp": now_iso(),
                    "context": input.message,
                    "score": c.get("score")
                }

                if not any(
                    r.get("career_id") == rec["career_id"]
                    for r in user_memory["recomendaciones"]
                    if r.get("career_id") is not None
                ):
                    user_memory["recomendaciones"].append(rec)



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
        safe_memory = normalize_for_json(user_memory)
        session_manager.save_profile(input.user_id, safe_memory)

        # 4️⃣ Marcamos fin de la transmisión
        yield "\n[END]\n"
    

    return StreamingResponse(
        generator(),
        media_type="text/plain"
    )

# --- RUTA DE EMERGENCIA PARA UNIVERSIDADES ---
@app.get("/universities")
async def get_universities(
    page: int = 1, 
    limit: int = 20, 
    pool = Depends(get_pool)
):
    offset = (page - 1) * limit

    # 1. Consulta REAL a la Base de Datos
    rows = await pool.fetch("""
        SELECT * FROM universities 
        ORDER BY id 
        LIMIT $1 OFFSET $2
    """, limit, offset)

    results = []
    for r in rows:
        # Convertimos la fila a diccionario para evitar errores si faltan columnas
        d = dict(r)

        results.append({
            "id": d.get("id"),
            "nombre": d.get("name", "Sin Nombre"), # Ajusta 'name' si la columna se llama distinto
            "tipo": d.get("type", "Institución"),
            "ubicacion": d.get("location", "Ecuador"),
            "imagen": d.get("url_logo", None), # Si es null, el frontend pondrá el placeholder
            "descripcion": d.get("description", "Sin descripción disponible."),
            "matchIA": 0, # Calcularemos esto luego con la IA
            "url": d.get("website", d.get("url", "#"))
        })

    return results
