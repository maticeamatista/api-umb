# models/producto.py
from pydantic import BaseModel
from typing import Optional

class Producto(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    stock: int

class Orden(BaseModel):
    producto_id: str
    cantidad: int
    cliente: str