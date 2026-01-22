from utils import clean_text


class BaseUniversityParser:
    university_name = ""
    city = ""

    def create_base_item(self, url: str) -> dict:
        return {
            "university": self.university_name,
            "city": self.city,
            "career_name": None,
            "faculty": None,
            "degree_title": None,
            "description": None,
            "duration": None,
            "modality": None,
            "mission": None,
            "vision": None,
            "objectives": None,
            "career_profile": None,
            "study_plan_pdf": None,
            "url": url
        }

    def clean(self, value):
        return clean_text(value)
