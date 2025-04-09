# main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes.auth_routes import router as auth_router
from routes.producto_routes import router as producto_router
from routes.orden_routes import router as orden_router

app = FastAPI()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(auth_router)
app.include_router(producto_router)
app.include_router(orden_router)

# Configurar plantillas
templates = Jinja2Templates(directory="templates")

# Manejo de excepciones globales
@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_exception_handler(request: Request, exc: Exception):
    return RedirectResponse(url="/auth/login", status_code=303)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/auth/login", status_code=303)