# services/producto_service.py
from models.producto import Producto
from db.database import database
from fastapi import HTTPException
from typing import Optional, List
from bson import ObjectId

async def obtener_productos() -> List[dict]:
    productos_collection = database.get_collection("productos")  # Eliminamos 'await'
    productos = await productos_collection.find().to_list(length=None)
    for producto in productos:
        producto["_id"] = str(producto["_id"])
    return productos

async def obtener_producto_por_id(producto_id: str) -> dict:
    productos_collection = database.get_collection("productos")  # Eliminamos 'await'
    try:
        producto = await productos_collection.find_one({"_id": ObjectId(producto_id)})
        if producto:
            producto["_id"] = str(producto["_id"])
            return producto
        return None
    except Exception:
        return None

async def insertar_producto(producto: Producto) -> dict:
    productos_collection = database.get_collection("productos")  # Eliminamos 'await'
    producto_dict = producto.dict(exclude_unset=True)
    result = await productos_collection.insert_one(producto_dict)
    return {"id": str(result.inserted_id), "mensaje": "Producto creado exitosamente"}

async def actualizar_producto(producto_id: str, producto: Producto) -> dict:
    productos_collection = database.get_collection("productos")  # Eliminamos 'await'
    try:
        result = await productos_collection.update_one(
            {"_id": ObjectId(producto_id)},
            {"$set": producto.dict(exclude_unset=True)}
        )
        if result.matched_count == 0:
            return {"mensaje": f"Producto con id {producto_id} no encontrado"}
        return {"mensaje": "Producto actualizado exitosamente"}
    except Exception:
        return {"mensaje": f"Producto con id {producto_id} no encontrado"}

async def eliminar_producto(producto_id: str) -> dict:
    productos_collection = database.get_collection("productos")  # Eliminamos 'await'
    try:
        result = await productos_collection.delete_one({"_id": ObjectId(producto_id)})
        if result.deleted_count == 0:
            return {"mensaje": f"Producto con id {producto_id} no encontrado"}
        return {"mensaje": "Producto eliminado exitosamente"}
    except Exception:
        return {"mensaje": f"Producto con id {producto_id} no encontrado"}

async def filtrar_productos(categoria: Optional[str] = None, min_price: float = 0.0) -> List[dict]:
    productos_collection = database.get_collection("productos")  # Eliminamos 'await'
    query = {}
    if categoria:
        query["category"] = categoria
    if min_price > 0:
        query["price"] = {"$gte": min_price}
    
    productos = await productos_collection.find(query).to_list(length=None)
    for producto in productos:
        producto["_id"] = str(producto["_id"])
    return productos