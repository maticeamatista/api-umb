from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Optional
from models.producto import Producto
from services.producto_service import (
    obtener_productos, obtener_producto_por_id, insertar_producto,
    actualizar_producto, eliminar_producto, filtrar_productos
)
from auth import get_current_user

router = APIRouter(prefix="/productos", tags=["Productos"])
templates = Jinja2Templates(directory="templates")

@router.get("/filtrar")
async def mostrar_productos(
    request: Request,
    categoria: Optional[str] = None,
    min_price: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    print(f"Accediendo a /productos/filtrar con usuario: {current_user}")
    try:
        min_price_float = float(min_price) if min_price else 0.0
    except (ValueError, TypeError):
        min_price_float = 0.0
    productos = await filtrar_productos(categoria, min_price_float)
    print(f"Productos obtenidos: {productos}")
    return templates.TemplateResponse("productos.html", {
        "request": request,
        "productos": productos,
        "categoria": categoria,
        "min_price": min_price if min_price else "",
        "current_user": current_user
    })

@router.get("/agregar")
async def mostrar_formulario_agregar(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("agregar_producto.html", {"request": request})

@router.get("/editar/{producto_id}")
async def mostrar_formulario_edicion(request: Request, producto_id: str, current_user: dict = Depends(get_current_user)):
    producto = await obtener_producto_por_id(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return templates.TemplateResponse("editar_producto.html", {
        "request": request,
        "producto": producto
    })

@router.get("/")
async def obtener_todos_productos(current_user: dict = Depends(get_current_user)):
    return await obtener_productos()

@router.get("/{producto_id}")
async def obtener_producto(producto_id: str, current_user: dict = Depends(get_current_user)):
    producto = await obtener_producto_por_id(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("/", status_code=201)
async def crear_producto(
    request: Request,
    name: str = Form(None),
    description: Optional[str] = Form(None),
    price: float = Form(None),
    category: Optional[str] = Form(None),
    stock: int = Form(None),
    producto: Optional[Producto] = Depends(lambda: None),
    current_user: dict = Depends(get_current_user)
):
    try:
        if name is not None:
            print(f"Datos del formulario: name={name}, price={price}, stock={stock}")
            producto = Producto(name=name, description=description, price=price, category=category, stock=stock)
            resultado = await insertar_producto(producto)
            print(f"Producto insertado: {resultado}")
            return RedirectResponse(url="/productos/filtrar", status_code=303)
        elif producto is not None:
            return await insertar_producto(producto)
        raise HTTPException(status_code=400, detail="Datos inválidos: no se proporcionaron datos válidos")
    except ValueError as e:
        print(f"Error de validación: {e}")
        if name is not None:
            return templates.TemplateResponse(
                "agregar_producto.html",
                {"request": request, "error": f"Error de validación: {str(e)}"}
            )
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(e)}")
    except Exception as e:
        print(f"Error al crear producto: {e}")
        if name is not None:
            return templates.TemplateResponse(
                "agregar_producto.html",
                {"request": request, "error": f"Error al crear producto: {str(e)}"}
            )
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {str(e)}")

@router.put("/{producto_id}")
async def editar_producto(producto_id: str, producto: Producto, current_user: dict = Depends(get_current_user)):
    resultado = await actualizar_producto(producto_id, producto)
    if "no encontrado" in resultado["mensaje"]:
        raise HTTPException(status_code=404, detail=resultado["mensaje"])
    return resultado

@router.delete("/{producto_id}")
async def borrar_producto(producto_id: str, current_user: dict = Depends(get_current_user)):
    resultado = await eliminar_producto(producto_id)
    if "no encontrado" in resultado["mensaje"]:
        raise HTTPException(status_code=404, detail=resultado["mensaje"])
    return resultado

@router.post("/editar/{producto_id}")
async def procesar_edicion(
    producto_id: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    category: Optional[str] = Form(None),
    stock: int = Form(...),
    current_user: dict = Depends(get_current_user)
):
    producto = Producto(name=name, description=description, price=price, category=category, stock=stock)
    resultado = await actualizar_producto(producto_id, producto)
    if "no encontrado" in resultado["mensaje"]:
        raise HTTPException(status_code=404, detail=resultado["mensaje"])
    return RedirectResponse(url="/productos/filtrar", status_code=303)

@router.post("/{producto_id}")
async def manejar_formulario_delete(producto_id: str, method: str = Form(None), current_user: dict = Depends(get_current_user)):
    if method == "DELETE":
        resultado = await eliminar_producto(producto_id)
        if "no encontrado" in resultado["mensaje"]:
            raise HTTPException(status_code=404, detail=resultado["mensaje"])
        return RedirectResponse(url="/productos/filtrar", status_code=303)
    raise HTTPException(status_code=400, detail="Método no soportado")