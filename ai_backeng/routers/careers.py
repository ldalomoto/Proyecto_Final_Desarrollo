from fastapi import APIRouter, Depends
from typing import List
from ai_backeng.schemas.career import CareerResponse
from ai_backeng.db.postgres import get_pool
from uuid import UUID

router = APIRouter(prefix="/careers", tags=["Careers"])

@router.get("/", response_model=List[CareerResponse])
async def get_careers(pool = Depends(get_pool)):

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
            c.image_url,
            u.name AS university_name
        FROM careers c
        LEFT JOIN universities u ON c.university_id = u.id
    """)

    careers = {}

    for r in rows:
        cid = str(r["id"])

        if cid not in careers:
            careers[cid] = {
                "id": r["id"],
                "nombre": r["career_name"],
                "area": r["faculty_name"],
                "imagen": r["image_url"],
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
