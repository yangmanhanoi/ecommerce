from datetime import datetime
from bson import ObjectId
class Author:
    def __init__(self, name: str, birth_year: int, nationality: str = "vi"):
        self.name = name
        self.birth_year = birth_year
        self.nationality = nationality
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            "name": self.name,
            "birth_year": self.birth_year,
            "nationality": self.nationality,
            "created_at": self.created_at
        }
class Book:
    def __init__(self,product_id: str, name: str, author_ids: list, publisher: str, isbn: str, pages: int, language: str, published_year: int):
        self.product_id = product_id
        self.name = name
        self.category = "book"  
        self.author_ids = [ObjectId(aid) for aid in author_ids]
        self.publisher = publisher
        self.isbn = isbn
        self.pages = pages
        self.language = language
        self.published_year = published_year
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "author_ids": self.author_ids,
            "publisher": self.publisher,
            "isbn": self.isbn,
            "pages": self.pages,
            "language": self.language,
            "published_year": self.published_year,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
