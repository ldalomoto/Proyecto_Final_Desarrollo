from fastapi import FastAPI, Header
from pydantic import BaseModel
from ai_backeng.db.postgres import init_db, get_pool
from ai_backeng.embeddings.embedding_provider import get_embedding
from ai_backeng.embeddings.blend import blend_embeddings
from ai_backeng.matching.get_best_careers import get_best_careers
from ai_backeng.agent import run_agent
from ai_backeng.memory.redis_manager import SessionManager
from ai_backeng.memory.extractor import extract_profile_updates

app = FastAPI()
session_manager = SessionManager()

class ChatInput(BaseModel):
    user_id: str  # Ahora identificamos al usuario
    message: str

@app.on_event("startup")
async def startup():
    await init_db()
@app.post("/chat")
async def chat(input: ChatInput):
    pool = await get_pool()
    
    # 1. Recuperamos memoria de Redis
    user_memory = session_manager.get_profile(input.user_id)

    # --- CAMBIO AQUÍ ---
    # 2. Llamamos al extractor nuevo
    # Ahora recibimos un diccionario con el perfil Y la bandera de intención
    extraction_result = extract_profile_updates(input.message, user_memory)
    
    # Actualizamos nuestra variable local con los datos limpios
    user_memory = extraction_result["profile_data"]
    
    # Verificamos si vale la pena gastar recursos en embeddings
    should_update_embedding = extraction_result["has_career_intent"]
    # -------------------

    # 3. Solo buscamos carreras si hay intención vocacional real
    # (Así evitas mezclar vectores cuando el usuario solo dice "Hola")
    if should_update_embedding:
        new_emb = get_embedding(input.message)
        
        # Mezclamos con lo anterior (Blend)
        current_emb = user_memory.get("user_embedding")
        if current_emb:
            user_memory["user_embedding"] = blend_embeddings(current_emb, new_emb)
        else:
            user_memory["user_embedding"] = new_emb

    # 4. Buscamos carreras (Solo si tenemos un embedding válido)
    careers = []
    if user_memory.get("user_embedding"):
        careers = await get_best_careers(
            pool,
            user_memory["user_embedding"],
            user_memory.get("preferencias", {}) # Asegúrate de que esto exista en tu JSON
        )

    # 5. El agente responde usando la memoria actualizada
    reply = run_agent(input.message, user_memory, careers)

    # 6. Guardamos en Redis el perfil FINAL (con el embedding nuevo si hubo cambios)
    session_manager.save_profile(input.user_id, user_memory)

    return {"reply": reply}
    