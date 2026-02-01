# ai_backeng/matching/get_best_careers.py

from ai_backeng.db.vector import to_pgvector
from ai_backeng.agent import normalize_modality, build_user_embedding_text
from ai_backeng.rerank.voyage_rerank import rerank_careers

async def get_best_careers(
    pool,
    user_embedding,
    preferences,
    recall_k: int = 40,
    final_k: int = 5
):
    async with pool.acquire() as conn:
        user_vec = to_pgvector(user_embedding)
        modality_filter = normalize_modality(preferences.get("modalidad"))

        query = """
            SELECT
                c.career_name,
                c.description,
                c.modality,
                c.duration,
                m.score
            FROM match_careers_by_embedding($1::vector, $2) m
            JOIN careers c ON c.id = m.career_id
            WHERE ($3::text IS NULL OR lower(unaccent(c.modality)) = $3)
            ORDER BY m.score DESC
            LIMIT $2;
        """

        rows = await conn.fetch(
            query,
            user_vec,
            recall_k,
            modality_filter
        )

        careers = [dict(r) for r in rows]

        # 🔥 RERANK SEMÁNTICO
        user_query = build_user_embedding_text({
            "intereses": preferences.get("intereses", []),
            "habilidades_percibidas": preferences.get("habilidades_percibidas", []),
            "materias_fuertes": preferences.get("materias_fuertes", [])
        })

        reranked = rerank_careers(
            user_query=user_query,
            careers=careers,
            top_k=final_k
        )

        return reranked
