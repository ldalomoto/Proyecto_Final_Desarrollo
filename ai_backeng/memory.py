def empty_profile():
    return {
        "nombre": None, # <--- Nuevo
        "intereses": [],
        "habilidades_percibidas": [],
        "preferencias": {
            "modalidad": None,
            "ciudad": None,
            "universidad_publica": None
        },
        "descripcion_libre": "",
        "user_embedding": None
    }