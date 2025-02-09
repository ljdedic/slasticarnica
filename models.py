from pydantic import BaseModel

class Proizvod(BaseModel):
    naziv: str
    opis: str = None
    cijena: float
    kategorija_id: int = None

class Kategorija(BaseModel):
    naziv: str
   