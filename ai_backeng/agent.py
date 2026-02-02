import os
from dotenv import load_dotenv
import google.generativeai as genai
from ai_backeng.prompt import SYSTEM_PROMPT
import unicodedata

# ------------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------------

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("No se encontró la GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-pro" # Excelente elección para estabilidad

GENERATION_CONFIG = {
    "temperature": 0.3,        # Un poco más baja para máxima fidelidad al texto
    "top_p": 0.95,             # Ayuda a que la selección de palabras sea coherente
    "max_output_tokens": 8192  # El máximo permitido para no cortar respuestas largas
}

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=GENERATION_CONFIG
)

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def format_profile_for_agent(profile: dict) -> str:
    preferencias = profile.get("preferencias", {})

    universidad_publica = preferencias.get("universidad_publica")
    universidad_texto = (
        "Sí" if universidad_publica is True
        else "No" if universidad_publica is False
        else "NO ESPECIFICADO"
    )

    return f"""
Nombre del usuario: {profile.get("nombre") or "NO ESPECIFICADO"}

Ciudad de residencia: {preferencias.get("ciudad") or "NO ESPECIFICADO"}

Preferencias educativas:
- Modalidad: {preferencias.get("modalidad") or "NO ESPECIFICADO"}
- Universidad pública: {universidad_texto}

Intereses del usuario:
{", ".join(profile.get("intereses", [])) or "NO ESPECIFICADO"}

Habilidades percibidas:
{", ".join(profile.get("habilidades_percibidas", [])) or "NO ESPECIFICADO"}

Materias fuertes:
{", ".join(profile.get("materias_fuertes", [])) or "NO ESPECIFICADO"}

Materias débiles:
{", ".join(profile.get("materias_debiles", [])) or "NO ESPECIFICADO"}

Descripción libre del usuario:
{profile.get("descripcion_libre") or "NO ESPECIFICADO"}
""".strip()


def format_careers(careers: list[dict], limit: int = 5) -> str:
    if not careers:
        return "No hay carreras aún."

    return "\n".join(
        f"- {c['career_name']} "
        f"(Modalidad: {c['modality']}, Duración: {c['duration']} semestres)\n"
        f"  {c['description'][:300]}"
        for c in careers[:limit]
    )


def build_user_embedding_text(profile: dict) -> str:
    """
    Genera el texto que se convertirá en embedding, incluyendo
    materias, habilidades e intereses.
    """
    partes = []

    if profile.get("intereses"):
        partes.append("Intereses: " + ", ".join(profile["intereses"]))
    if profile.get("habilidades_percibidas"):
        partes.append("Habilidades: " + ", ".join(profile["habilidades_percibidas"]))
    if profile.get("materias_fuertes"):
        partes.append("Materias fuertes: " + ", ".join(profile["materias_fuertes"]))
    if profile.get("materias_debiles"):
        partes.append("Materias débiles: " + ", ".join(profile["materias_debiles"]))

    return ". ".join(partes)


def normalize_modality(modality):
    """
    Convierte modalidad a minúsculas, sin tildes, y asegura que sea solo
    una de las opciones válidas: 'presencial', 'dual', 'hibrida'.
    """
    import unicodedata

    if not modality:
        return None

    # Si viene lista, tomar el primer elemento
    if isinstance(modality, list):
        modality = modality[0]

    # Normalizar a string y quitar tildes
    modality = str(modality).lower().strip()
    modality = ''.join(
        c for c in unicodedata.normalize('NFD', modality)
        if unicodedata.category(c) != 'Mn'
    )

    # Filtrar solo opciones válidas
    if modality not in ('presencial', 'dual', 'hibrida'):
        return None

    return modality

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def merge_lists(existing, new):
    """
    Combina dos listas eliminando duplicados y manejando None.
    """
    return list(set(existing or []) | set(new or []))


# ------------------------------------------------------------------
# AGENTE PRINCIPAL
# ------------------------------------------------------------------

def run_agent(
    user_message: str,
    profile: dict,
    careers: list[dict],
    should_greet: bool
) -> str:
    chunks = []
    for chunk in run_agent_stream(
        user_message,
        profile,
        careers,
        should_greet
    ):
        chunks.append(chunk)
    return "".join(chunks)


def run_agent_stream(
    user_message: str,
    profile: dict,
    careers: list[dict],
    should_greet: bool
):
    greeting_rule = (
        "Saluda brevemente al usuario usando su nombre."
        if should_greet
        else "NO saludes ni menciones reencuentros. Continúa la conversación directamente."
    )

    full_prompt = f"""
{SYSTEM_PROMPT}

INSTRUCCIONES IMPORTANTES:
- Usa SIEMPRE la información del PERFIL ACTUAL.
- NO preguntes datos que ya estén especificados.
- SOLO pregunta por datos marcados como "NO ESPECIFICADO".
- Personaliza la respuesta usando el nombre si existe.
- Ten en cuenta ciudad, modalidad y tipo de universidad al recomendar.

INSTRUCCIÓN DE SALUDO:
{greeting_rule}

============================
MENSAJE DEL USUARIO
============================
{user_message}

============================
PERFIL ACTUAL DEL USUARIO (MEMORIA)
============================
{format_profile_for_agent(profile)}

============================
CARRERAS DISPONIBLES
============================
{format_careers(careers)}
""".strip()

    stream = model.generate_content(
        full_prompt,
        stream=True
    )
    
    for chunk in stream:
        print("#######################################################")
        print(chunk)
        print("#######################################################")

        if chunk.text:
            yield chunk


