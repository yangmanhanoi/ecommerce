from datetime import datetime

class Clothes:
    def __init__(self, product_id: str, brand_id: str, material: str, size: str, color: str, gender: str):
        self.product_id = product_id
        self.brand_id = brand_id
        self.material = material
        self.size = size
        self.color = color
        self.gender = gender
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            "product_id": self.product_id,
            "brand_id": self.brand_id,
            "material": self.material,
            "size": self.size,
            "color": self.color,
            "gender": self.gender,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class Brand:
    def __init__(self, name: str, origin_country: str = "", description: str = ""):
        self.name = name
        self.origin_country = origin_country
        self.description = description

    def to_dict(self):
        return {
            "name": self.name,
            "origin_country": self.origin_country,
            "description": self.description
        }