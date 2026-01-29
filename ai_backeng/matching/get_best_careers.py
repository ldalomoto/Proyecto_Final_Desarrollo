from ai_backeng.db.vector import to_pgvector
from ai_backeng.agent import normalize_modality

async def get_best_careers(pool, user_embedding, preferences, top_k=5):
    async with pool.acquire() as conn:
        user_vec = to_pgvector(user_embedding)

        modality_filter = normalize_modality(preferences.get("modalidad"))

        query = """
            SELECT c.career_name, c.description, c.modality, c.duration, m.score
            FROM match_careers_by_embedding($1::vector, $2) m
            JOIN careers c ON c.id = m.career_id
            WHERE ($3::text IS NULL OR lower(unaccent(c.modality)) = $3)
            ORDER BY m.score DESC
            LIMIT $2;
        """

        rows = await conn.fetch(query, user_vec, top_k, modality_filter)
        return [dict(r) for r in rows]
