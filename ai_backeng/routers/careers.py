from fastapi import APIRouter, Depends, Query
from typing import List
from ai_backeng.schemas.career import CareerResponse
from ai_backeng.db.postgres import get_pool

router = APIRouter(
    prefix="/careers",
    tags=["careers"]
)

@router.get("/", response_model=List[CareerResponse])
async def get_careers(
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1, le=20),
    pool = Depends(get_pool)
):
    offset = (page - 1) * limit

    rows = await pool.fetch("""
        SELECT
            c.id,
            c.career_name,
            c.faculty_name,
            c.description,
            c.duration,
            c.modality,
            c.cost,
            c.career_url,
            NULL AS imagen,
            u.name AS university_name
        FROM careers c
        LEFT JOIN universities u ON c.university_id = u.id
        ORDER BY c.career_name
        LIMIT $1 OFFSET $2
    """, limit, offset)

    careers = {}

    for r in rows:
        cid = str(r["id"])

        if cid not in careers:
            careers[cid] = {
                "id": r["id"],
                "nombre": r["career_name"],
                "area": r["faculty_name"],
                "imagen": r["imagen"],
                "descripcion": r["description"],
                "duracion": r["duration"],
                "modalidad": r["modality"],
                "salarioPromedio": r["cost"],
                "universidades": [],
                "url": r["career_url"]
            }

        if r["university_name"]:
            careers[cid]["universidades"].append(r["university_name"])

    return list(careers.values())
