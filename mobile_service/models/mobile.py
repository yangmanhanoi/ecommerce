from datetime import datetime
class Mobile:
    def __init__(self, product_id: str, name: str, brand: str, model: str, ram: str, storage: str,
                 battery: str, screen_size: str, os: str):
        self.product_id = product_id  # Tham chiếu đến Product
        self.name = name
        self.brand = brand
        self.model = model
        self.ram = ram
        self.storage = storage
        self.battery = battery
        self.screen_size = screen_size
        self.os = os
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "brand": self.brand,
            "model": self.model,
            "ram": self.ram,
            "storage": self.storage,
            "battery": self.battery,
            "screen_size": self.screen_size,
            "os": self.os,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }