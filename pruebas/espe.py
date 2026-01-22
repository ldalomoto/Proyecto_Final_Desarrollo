from utils import get_soup
from base_university import BaseUniversityParser
import json

BASE_URL = "https://www.uce.edu.ec/grado"

class UCEParser(BaseUniversityParser):
    university_name = "Universidad Central del Ecuador"
    city = "Quito"

    def get_career_links(self):
        soup = get_soup(BASE_URL)
        return [a["href"] for a in soup.select("a[href*='web']")]

    def parse_career(self, url):
        soup = get_soup(url)
        item = self.create_base_item(url)

        item["career_name"] = self.clean(soup.select_one("h1"))
        item["description"] = self.clean(
            " ".join(p.get_text() for p in soup.select("p"))
        )

        return item



def main():
    parser = UCEParser()
    careers = []

    for url in parser.get_career_links():
        try:
            careers.append(parser.parse_career(url))
        except Exception as e:
            print(f"❌ {url}: {e}")

    with open("espe_carreras.json", "w", encoding="utf-8") as f:
        json.dump(careers, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
