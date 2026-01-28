import redis
import json
import os

class SessionManager:
    def __init__(self):
        # En AWS/Producción: usarás la URL de ElastiCache
        self.redis = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"), 
            decode_responses=True
        )
        self.ttl = 86400  # Aumentamos a 24 horas para que no te olvides del usuario tan rápido

    def get_profile(self, user_id: str):
        """Recupera la memoria del usuario. Si no existe, crea una nueva."""
        data = self.redis.get(f"session:{user_id}")
        if data:
            return json.loads(data)
        return self._empty_profile()

    def save_profile(self, user_id: str, profile: dict):
        """
        Sobreescribe la sesión con el perfil actualizado.
        IMPORTANTE: El 'merge' de datos (no borrar lo anterior) 
        debe hacerse en el extractor.py antes de llamar a esta función.
        """
        self.redis.setex(f"session:{user_id}", self.ttl, json.dumps(profile))

    def _empty_profile(self):
        """Estructura inicial completa."""
        return {
            "nombre": None,                # <--- Faltaba esto
            "intereses": [],
            "habilidades_percibidas": [],
            "preferencias": {
                "modalidad": None,
                "ciudad": None,
                "universidad_publica": None # <--- Faltaba esto
            },
            "descripcion_libre": "",
            "user_embedding": None
        }