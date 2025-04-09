from fastapi import HTTPException
from models.producto import Orden
from db.database import database
from bson import ObjectId  # Importar ObjectId para convertir la cadena a ObjectId

async def crear_orden(orden: Orden):
    try:
        # Obtener la colección de órdenes y productos
        ordenes_collection = database.get_collection("ordenes")
        productos_collection = database.get_collection("productos")

        # Convertir producto_id de cadena a ObjectId
        try:
            producto_id = ObjectId(orden.producto_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"ID de producto inválido: {str(e)}")

        # Verificar si el producto existe y tiene suficiente stock
        producto = await productos_collection.find_one({"_id": producto_id})
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        if producto["stock"] < orden.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")

        # Crear la orden
        orden_dict = orden.dict()
        # Asegurarse de que el producto_id en la orden también sea un ObjectId
        orden_dict["producto_id"] = producto_id
        result = await ordenes_collection.insert_one(orden_dict)
        orden_id = str(result.inserted_id)

        # Actualizar el stock del producto
        nuevo_stock = producto["stock"] - orden.cantidad
        await productos_collection.update_one(
            {"_id": producto_id},
            {"$set": {"stock": nuevo_stock}}
        )

        return {"id": orden_id, "mensaje": "Orden creada exitosamente, stock actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear orden: {str(e)}")