from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from models.producto import Orden
from services.orden_service import crear_orden
from fastapi import HTTPException
from auth import get_current_user

router = APIRouter(prefix="/ordenes", tags=["Ordenes"])

@router.post("/", response_class=HTMLResponse)
async def registrar_orden_form(
    request: Request,
    producto_id: str = Form(...),
    cantidad: int = Form(...),
    current_user: dict = Depends(get_current_user)
):
    # Usar el nombre de usuario del usuario autenticado como cliente
    cliente = current_user["username"]
    print(f"Creando orden para el cliente: {cliente}")
    orden = Orden(producto_id=producto_id, cantidad=cantidad, cliente=cliente)
    try:
        resultado = await crear_orden(orden)
        print(f"Orden creada exitosamente: {resultado}")
        # Mostrar un mensaje de éxito antes de redirigir
        return HTMLResponse(
            content="""
            <h2 style='color:green;'>Orden creada exitosamente</h2>
            <p>Redirigiendo a la lista de productos...</p>
            <script>
                setTimeout(() => { window.location.href = "/productos/filtrar"; }, 2000);
            </script>
            """
        )
    except HTTPException as e:
        print(f"Error al crear orden: {e.detail}")
        return HTMLResponse(
            f"<h2 style='color:red;'>Error: {e.detail}</h2><a href='/productos/filtrar'>Volver</a>"
        )