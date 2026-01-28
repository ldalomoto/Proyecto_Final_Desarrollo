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
    
    # 1. Recuperamos lo que Redis sabe de 'user1'
    user_memory = session_manager.get_profile(input.user_id)

    # 2. El extractor lee el mensaje y actualiza el JSON (Merge)
    # Si el mensaje es "Me llamo Lenin", el JSON ahora tendrá nombre: "Lenin" 
    # y mantendrá ciudad: "Quito" de la sesión anterior.
    user_memory = extract_profile_updates(input.message, user_memory)

    # 3. Solo buscamos carreras si ya tenemos intereses o el embedding
    new_emb = get_embedding(input.message)
    user_memory["user_embedding"] = blend_embeddings(
        user_memory.get("user_embedding"),
        new_emb
    )

    careers = await get_best_careers(
        pool,
        user_memory["user_embedding"],
        user_memory["preferencias"]
    )

    # 4. Le pasamos al agente el perfil YA ACTUALIZADO
    reply = run_agent(input.message, user_memory, careers)

    # 5. Guardamos en Redis el perfil con los nuevos datos (Nombre, intereses, etc)
    session_manager.save_profile(input.user_id, user_memory)

    return {"reply": reply}