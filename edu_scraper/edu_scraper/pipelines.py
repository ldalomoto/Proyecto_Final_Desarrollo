import json


class JsonArrayPipeline:
    def open_spider(self, spider):
        self.items = []

    def close_spider(self, spider):
        with open(f"/home/david/Documentos/UCE/DESARROLLO/Proyecto_Final/Proyecto_Final_Desarrollo/data/{spider.name}_careers.json", "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item
