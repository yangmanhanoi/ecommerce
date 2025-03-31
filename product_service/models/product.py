from abc import ABC, abstractmethod
from datetime import datetime
class Product(ABC):

    def __init__(self, name: str, category: str, price: float, stock: int):
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "category": self.category,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class Mobile(Product):
    def __init__(self, name, price, stock, ram, storage, battery):
        super().__init__(name, "Mobile", price, stock)
        self.ram = ram
        self.storage = storage
        self.battery = battery
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "ram": self.ram,
            "storage": self.storage,
            "battery": self.battery
        })
        return data

class Clothes(Product):
    def __init__(self, name, price, stock, size, color, material):
        super().__init__(name, "Clothes", price, stock)
        self.size = size
        self.color = color
        self.material = material
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "size":self.size,
            "color": self.color,
            "material": self.material
        
        })
        return data

class Book(Product):
    def __init__(self, name, price, stock, author, isbn, published_year):
        super().__init__(name, "Book", price, stock)
        self.author = author
        self.isbn = isbn
        self.published_year = published_year

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "author": self.author,
            "isbn": self.isbn,
            "published_year": self.published_year
        })
        return data

class Comment:
    def __init__(self, book_id, comment, evaluate):
        self.book_id = book_id
        self.comment = comment
        self.evaluate = evaluate
    
    def to_dict(self):
        return {
            "book_id": self.book_id,
            "comment": self.comment,
            "evaluate": self.evaluate
        }