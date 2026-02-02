import json
import hashlib
import re
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from huggingface_hub import login

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "data_unificada"
OUTPUT_DIR = BASE_DIR / "data_skills_final"
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def setup_model():
    print(f"--- Iniciando carga en dispositivo: {DEVICE} ---")
    login() # Pedirá el token solo la primera vez en la terminal
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto"
    )
    print("✅ Modelo cargado con éxito.")
    return model, tokenizer

def limpiar_json_pro(texto_sucio):
    """
    Extrae el JSON y limpia errores comunes de sintaxis de LLMs.
    """
    try:
        # Extraer lo que esté entre las primeras y últimas llaves
        match = re.search(r"\{.*\}", texto_sucio, re.DOTALL)
        if not match:
            return None
        
        json_str = match.group(0)
        # Quita comas sobrantes antes de cerrar listas o diccionarios
        json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
        
        return json.loads(json_str)
    except:
        return None

def generar_prompt_carrera(career, materias_bloque):
    materias_texto = "\n".join(f"- {m}" for m in materias_bloque)
    num_skills = 1 if len(materias_bloque) <= 2 else (5 if len(materias_bloque) <= 5 else 10)

    return f"""<|begin_of_text|><|system|>
Eres un orientador vocacional. Respondes UNICAMENTE en JSON. Formato: {{"skills": ["habilidad"]}}<|end|>
<|user|>
Carrera: {career.get('career_name')}
Universidad: {career.get('university_name')}
Materias: {materias_texto}
Genera {num_skills} habilidades clave.
<|end|>
<|assistant|>
"""

def inferir_skills(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(DEVICE)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=400,
            do_sample=True,
            temperature=0.1,
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Intentar parsear
    data = limpiar_json_pro(decoded)
    
    # Validar que sea una lista de strings
    if data and isinstance(data.get("skills"), list):
        # Filtrar solo elementos que sean strings para evitar el AttributeError
        return [str(s) for s in data["skills"] if s]
    
    return []

def main():
    model, tokenizer = setup_model()
    BLOQUE_SIZE = 10
    EXCLUDE_KEYWORDS = ["titulación", "práctica", "vinculación", "optativa", "itinerario"]

    json_files = list(INPUT_DIR.glob("*.json"))
    if not json_files:
        print(f"❌ No se encontraron archivos en {INPUT_DIR}")
        return

    resultado_final = []

    for archivo in json_files:
        print(f"\n📂 Procesando archivo: {archivo.name}")
        with open(archivo, "r", encoding="utf-8") as f:
            try:
                careers = json.load(f)
            except:
                print(f"⚠️ Error leyendo {archivo.name}. Saltando...")
                continue

        for career in careers:
            career_name = career.get("career_name", "Sin Nombre")
            print(f"  🎓 Analizando: {career_name}")
            
            # Limpieza de materias
            subjects_raw = career.get("subjects", [])
            materias = []
            for sub in subjects_raw:
                name = sub.get("name")
                if name and not any(kw in name.lower() for kw in EXCLUDE_KEYWORDS):
                    materias.append(name)

            if not materias:
                continue

            all_skills = set()
            for i in range(0, len(materias), BLOQUE_SIZE):
                bloque = materias[i:i+BLOQUE_SIZE]
                print(f"    ⚡ Bloque {i//BLOQUE_SIZE + 1}...")
                
                prompt = generar_prompt_carrera(career, bloque)
                skills_bloque = inferir_skills(model, tokenizer, prompt)
                
                for sk in skills_bloque:
                    # Aquí es donde fallaba: ahora nos aseguramos que sk sea string
                    clean_sk = str(sk).strip().lower()
                    if clean_sk:
                        all_skills.add(clean_sk)

            resultado_final.append({
                "career_id": career.get("career_id", "id_gen_" + hashlib.md5(career_name.encode()).hexdigest()[:6]),
                "career_name": career_name,
                "university_name": career.get("university_name"),
                "career_general_skills": sorted(list(all_skills))
            })

    # Guardado final
    output_path = OUTPUT_DIR / "careers_skills_ecuador.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ PROCESO FINALIZADO. Resultados en: {output_path}")

if __name__ == "_main_":
    main()