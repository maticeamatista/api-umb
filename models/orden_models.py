from pydantic import BaseModel

class Orden(BaseModel):
    producto_id: str
    cantidad: int
    cliente: str
