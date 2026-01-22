from urllib.parse import urljoin
import json
from utils import get_soup
from base_university import BaseUniversityParser


BASE_URL = "https://www.espol.edu.ec"


class EspolParser(BaseUniversityParser):
    university_name = "Escuela Superior Politécnica del Litoral"
    city = "Guayaquil"

    def get_career_links(self):
        soup = get_soup(f"{BASE_URL}/es/educacion/grado")

        links = set()
        for a in soup.select("a[href]"):
            href = a.get("href")
            if href and "/carreras-de-grado/" in href:
                links.add(urljoin(BASE_URL, href))

        return list(links)

    def parse_career(self, url: str) -> dict:
        soup = get_soup(url)
        item = self.create_base_item(url)

        # =========================
        # DATOS PRINCIPALES
        # =========================
        h1 = soup.select_one("h1")
        item["career_name"] = self.clean(h1) if h1 else None

        item["description"] = self.clean(
            " ".join(
                p.get_text()
                for p in soup.select(".field--name-body p")
            )
        )

        # =========================
        # INFORMACIÓN ACADÉMICA
        # =========================
        for block in soup.select(".field"):
            text = block.get_text(" ", strip=True).lower()

            if "duración" in text:
                item["duration"] = self.clean(block)

            if "modalidad" in text:
                item["modality"] = self.clean(block)

        return item


def main():
    parser = EspolParser()
    career_links = parser.get_career_links()

    print(f"Carreras encontradas: {len(career_links)}\n")

    careers = []

    for url in career_links:
        try:
            career = parser.parse_career(url)
            careers.append(career)
            print(f"✔ {career.get('career_name')}")

        except Exception as e:
            print(f"❌ Error en {url}: {e}")

    # 📌 Guardado JSON estructurado
    with open("espol_carreras.json", "w", encoding="utf-8") as f:
        json.dump(careers, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
