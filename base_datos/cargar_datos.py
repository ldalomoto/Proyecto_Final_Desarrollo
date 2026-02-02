#import os
#import json
#import psycopg2
#from dotenv import load_dotenv
#
#load_dotenv()
#
#import re
#import unicodedata
#
#def normalize_text(text: str) -> str:
#    if not text:
#        return ""
#    text = unicodedata.normalize("NFD", text)
#    text = text.encode("ascii", "ignore").decode("utf-8")
#    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
#    return text.upper().strip("_")
#
#def build_career_id(career: dict) -> str:
#    university = normalize_text(career.get("university_name"))
#    modality = normalize_text(career.get("modality"))
#    career_name = normalize_text(career.get("career_name"))
#
#    return f"{university}_{modality}_{career_name}"
#
#
## Conexión a PostgreSQL
#conn = psycopg2.connect(
#    host=os.getenv("DB_HOST"),
#    port=os.getenv("DB_PORT"),
#    user=os.getenv("DB_USER"),
#    password=os.getenv("DB_PASSWORD"),
#    dbname=os.getenv("DB_NAME")
#)
#cur = conn.cursor()
#
## Crear tablas si no existen
#def create_tables():
#    cur.execute("""
#    CREATE TABLE IF NOT EXISTS universities (
#        id SERIAL PRIMARY KEY,
#        name TEXT UNIQUE,
#        type TEXT,
#        contact TEXT
#    );
#    """)
#    cur.execute("""
#    CREATE TABLE IF NOT EXISTS careers (
#        id SERIAL PRIMARY KEY,
#        career_id TEXT UNIQUE,
#        university_id INT REFERENCES universities(id),
#        career_name TEXT,
#        faculty_name TEXT,
#        degree_title TEXT,
#        description TEXT,
#        modality TEXT,
#        duration TEXT,
#        cost TEXT,
#        career_url TEXT,
#        study_plan_name TEXT,
#        study_plan_pdf TEXT,
#        data_collection_date DATE
#    );
#    """)
#    cur.execute("""
#    CREATE TABLE IF NOT EXISTS subjects (
#        id SERIAL PRIMARY KEY,
#        career_id INT REFERENCES careers(id),
#        code TEXT,
#        name TEXT,
#        semester INT
#    );
#    """)
#    cur.execute("""
#    CREATE TABLE IF NOT EXISTS career_locations (
#        id SERIAL PRIMARY KEY,
#        career_id INT REFERENCES careers(id),
#        location TEXT
#    );
#    """)
#    conn.commit()
#
## Funciones para insertar datos
#def get_or_create_university(name, utype, contact):
#    cur.execute("SELECT id FROM universities WHERE name=%s", (name,))
#    res = cur.fetchone()
#    if res:
#        return res[0]
#
#    cur.execute(
#        "INSERT INTO universities (name, type, contact) VALUES (%s,%s,%s) RETURNING id",
#        (name, utype, contact)
#    )
#    university_id = cur.fetchone()[0]
#    conn.commit()
#    return university_id
#
#def insert_career(career, university_id):
#    career_code = career.get("career_id")
#
#    if not career_code:
#        career_code = build_career_id(career)
#
#    cur.execute("""
#    INSERT INTO careers (
#        career_id, university_id, career_name, faculty_name, degree_title, description,
#        modality, duration, cost, career_url, study_plan_name, study_plan_pdf, data_collection_date
#    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#    ON CONFLICT (career_id) DO UPDATE SET
#        university_id = EXCLUDED.university_id,
#        career_name = EXCLUDED.career_name
#    RETURNING id
#    """, (
#        career_code,
#        university_id,
#        career["career_name"],
#        career.get("faculty_name"),
#        career.get("degree_title"),
#        career.get("description"),
#        career.get("modality"),
#        career.get("duration"),
#        str(career.get("cost")),
#        career.get("career_url"),
#        career.get("study_plan_name"),
#        career.get("study_plan_pdf"),
#        career.get("data_collection_date")
#    ))
#
#    career_id = cur.fetchone()[0]
#    conn.commit()
#    return career_id
#
#
#def insert_subjects(career_id, subjects):
#    for s in subjects:
#        cur.execute("""
#        INSERT INTO subjects (career_id, code, name, semester)
#        VALUES (%s,%s,%s,%s)
#        """, (career_id, s.get("code"), s["name"], s.get("semester")))
#    conn.commit()
#
#def insert_locations(career_id, locations):
#    for loc in locations:
#        cur.execute("""
#        INSERT INTO career_locations (career_id, location)
#        VALUES (%s,%s)
#        """, (career_id, loc))
#    conn.commit()
#
## Cargar JSON
#def load_json(path):
#    with open(path, encoding="utf-8") as f:
#        return json.load(f)
#
## Procesar archivo completo
#def process_file(path):
#    create_tables()
#    careers = load_json(path)
#
#    for c in careers:
#        university_id = get_or_create_university(
#            c["university_name"],
#            c.get("university_type"),
#            c.get("university_contact")
#        )
#        career_id = insert_career(c, university_id)
#        insert_locations(career_id, c.get("locations", []))
#        insert_subjects(career_id, c.get("subjects", []))
#        print(f"✔ {c['career_name']}")
#
#if __name__ == "__main__":
#    process_file("/app/Data_UniDream/data_borradores/ECOTEC.json")  # Cambia a la ruta de tu JSON
#    cur.close()
#    conn.close()
#

#import os
#import psycopg2
#from dotenv import load_dotenv
#import voyageai
#
## ======================
## CONFIG
## ======================
#
#load_dotenv()
#
## Embeddings
#PROVIDER = os.getenv("EMBEDDING_PROVIDER", "voyage")
#VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
#
#if not VOYAGE_API_KEY:
#    raise RuntimeError("VOYAGE_API_KEY not set in .env")
#
#voyageai.api_key = VOYAGE_API_KEY
#
#EMBEDDING_MODEL_NAME = "voyage-4-lite"
#EMBEDDING_DIM = 1024
#
#client = voyageai.Client()
#
## PostgreSQL
#conn = psycopg2.connect(
#    host=os.getenv("DB_HOST"),
#    port=os.getenv("DB_PORT"),
#    user=os.getenv("DB_USER"),
#    password=os.getenv("DB_PASSWORD"),
#    dbname=os.getenv("DB_NAME")
#)
#cur = conn.cursor()
#
## ======================
## EMBEDDINGS
## ======================
#
#def get_embedding(text: str) -> list[float]:
#    if PROVIDER != "voyage":
#        raise RuntimeError("Embedding provider not supported")
#
#    response = client.embed(
#        texts=[text],
#        model=EMBEDDING_MODEL_NAME
#    )
#    return response.embeddings[0]
#
## ======================
## DB OPERATIONS
## ======================
#
#def fetch_all_skills(batch_size, offset):
#    cur.execute("""
#        SELECT id, normalized_name
#        FROM skills
#        ORDER BY id
#        LIMIT %s OFFSET %s
#    """, (batch_size, offset))
#    return cur.fetchall()
#
#def update_skill_embedding(skill_id: int, embedding: list[float]):
#    cur.execute("""
#        UPDATE skills
#        SET embedding = %s::vector,
#            embedding_model = %s
#        WHERE id = %s
#    """, (
#        embedding,
#        EMBEDDING_MODEL_NAME,
#        skill_id
#    ))
#
## ======================
## MAIN
## ======================
#
#def reembed_all_skills(batch_size=20):
#    offset = 0
#    total = 0
#
#    while True:
#        rows = fetch_all_skills(batch_size, offset)
#        if not rows:
#            break
#
#        for skill_id, normalized_name in rows:
#            try:
#                embedding = get_embedding(normalized_name)
#
#                if len(embedding) != EMBEDDING_DIM:
#                    raise ValueError("Dimensión incorrecta del embedding")
#
#                update_skill_embedding(skill_id, embedding)
#                total += 1
#                print(f"✔ Re-embedded skill {skill_id}: {normalized_name}")
#
#            except Exception as e:
#                print(f"✖ Error en skill {skill_id}: {e}")
#
#        conn.commit()
#        offset += batch_size
#
#    print(f"\n✅ Total skills re-embebidas: {total}")
#
## ======================
## ENTRYPOINT
## ======================
#
#if __name__ == "__main__":
#    reembed_all_skills(batch_size=16)
#    cur.close()
#    conn.close()
#


import os
import re
import psycopg2
import unicodedata
from dotenv import load_dotenv
import voyageai

# ======================
# CONFIG
# ======================

load_dotenv()

# Embeddings
PROVIDER = os.getenv("EMBEDDING_PROVIDER", "voyage")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

if not VOYAGE_API_KEY:
    raise RuntimeError("VOYAGE_API_KEY not set in .env")

voyageai.api_key = VOYAGE_API_KEY

EMBEDDING_MODEL_NAME = "voyage-4-lite"
EMBEDDING_DIM = 1024

client = voyageai.Client()

# PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME")
)
cur = conn.cursor()

# ======================
# NORMALIZACIÓN
# ======================

ROMAN_PATTERN = r"\b(i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii)\b"

def normalize_subject_name(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # quitar acentos
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    # eliminar numeros romanos
    text = re.sub(ROMAN_PATTERN, " ", text)

    # eliminar numeros arabigos
    text = re.sub(r"\d+", " ", text)

    # eliminar caracteres no alfabeticos
    text = re.sub(r"[^a-z\s]", " ", text)

    # limpiar espacios
    text = " ".join(text.split())

    return text.strip()

# ======================
# EMBEDDINGS
# ======================

def get_embedding(text: str) -> list[float]:
    if PROVIDER != "voyage":
        raise RuntimeError("Embedding provider not supported")

    response = client.embed(
        texts=[text],
        model=EMBEDDING_MODEL_NAME
    )
    return response.embeddings[0]

# ======================
# DB OPERATIONS
# ======================

def fetch_all_subjects(batch_size, offset):
    cur.execute("""
        SELECT id, name
        FROM subjects
        ORDER BY id
        LIMIT %s OFFSET %s
    """, (batch_size, offset))
    return cur.fetchall()

def update_subject(subject_id, normalized_name, embedding):
    cur.execute("""
        UPDATE subjects
        SET normalized_name = %s,
            embedding = %s::vector,
            embedding_model = %s
        WHERE id = %s
    """, (
        normalized_name,
        embedding,
        EMBEDDING_MODEL_NAME,
        subject_id
    ))

# ======================
# MAIN
# ======================

def reembed_all_subjects(batch_size=20):
    offset = 0
    total = 0

    while True:
        rows = fetch_all_subjects(batch_size, offset)
        if not rows:
            break

        for subject_id, name in rows:
            try:
                normalized = normalize_subject_name(name)

                if not normalized:
                    print(f"⚠ Nombre vacío tras normalizar: {name}")
                    continue

                embedding = get_embedding(normalized)

                if len(embedding) != EMBEDDING_DIM:
                    raise ValueError("Dimensión incorrecta del embedding")

                update_subject(subject_id, normalized, embedding)
                total += 1

                print(f"✔ {subject_id}: {name} → {normalized}")

            except Exception as e:
                print(f"✖ Error en subject {subject_id}: {e}")

        conn.commit()
        offset += batch_size

    print(f"\n✅ Total materias re-embebidas: {total}")

# ======================
# ENTRYPOINT
# ======================

if __name__ == "__main__":
    reembed_all_subjects(batch_size=16)
    cur.close()
    conn.close()
