import redis
import json
import os
from datetime import datetime, timezone


class SessionManager:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

        # 24 horas
        self.ttl = 60 * 60 * 24

        # Test rápido de conexión (falla rápido si Redis no está)
        try:
            self.redis.ping()
        except redis.exceptions.ConnectionError as e:
            raise RuntimeError("No se pudo conectar a Redis") from e

    def get_profile(self, user_id: str):
        """Recupera la memoria del usuario. Si no existe, crea una nueva."""
        data = self.redis.get(self._key(user_id))
        if data:
            return json.loads(data)
        return self._empty_profile()

    def save_profile(self, user_id: str, profile: dict):
        """
        Sobreescribe la sesión con el perfil actualizado.
        El merge debe hacerse antes.
        """
        self.redis.setex(
            self._key(user_id),
            self.ttl,
            json.dumps(profile, ensure_ascii=False)
        )

    def delete(self, user_id: str):
        self.redis.delete(self._key(user_id))

    def _key(self, user_id: str) -> str:
        return f"session:{user_id}"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _empty_profile(self):
        now = self._now()
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
            "meta": {
                "created_at": now,
                "last_seen_at": now,
                "last_greeted_at": None,
                "message_count": 0
            }
        }

