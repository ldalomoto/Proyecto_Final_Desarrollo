from datetime import datetime,timezone

def empty_profile():
    return {
        "nombre": None,
        "intereses": [],
        "habilidades_percibidas": [],
        "preferencias": {
            "modalidad": None,
            "ciudad": None,
            "universidad_publica": None
        },
        "descripcion_libre": "",
        "user_embedding": None,
        "materias_fuertes": [],
        "materias_debiles": [],
        "meta": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
            "last_greeted_at": None,
            "message_count": 0
        },
        "recomendaciones": []
    }
