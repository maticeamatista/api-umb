from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from jose import jwt, JWTError
from auth import create_access_token, get_user, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, register_user, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Autenticación"])
templates = Jinja2Templates(directory="templates")

# Mostrar formulario de login
@router.get("/login")
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Procesar login y generar token
@router.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Intento de inicio de sesión con username: {form_data.username}")
    user = await get_user(form_data.username)
    if not user:
        print("Usuario no encontrado")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario no encontrado"},
            status_code=401
        )

    if not verify_password(form_data.password, user["hashed_password"]):
        print("Contraseña incorrecta")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Contraseña incorrecta"},
            status_code=401
        )

    print("Credenciales correctas, generando token...")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    # Para navegadores: almacenar el token en una cookie y redirigir a la página de ingreso de token
    if "text/html" in request.headers.get("accept", ""):
        print("Redirigiendo a /auth/enter-token")
        response = RedirectResponse(url="/auth/enter-token", status_code=303)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Cambia a True si usas HTTPS
            samesite="lax",
            path="/",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Expiración en segundos
        )
        print(f"Cookie access_token establecida: {access_token}")
        return response
    # Para clientes API (como Postman): devolver el token en el cuerpo
    else:
        print("Devolviendo token en JSON para cliente API")
        return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})

# Nueva ruta para mostrar el formulario de ingreso de token
@router.get("/enter-token")
async def show_enter_token_form(request: Request):
    return templates.TemplateResponse("enter_token.html", {"request": request})

# Nueva ruta para procesar el token ingresado
@router.post("/verify-token")
async def verify_token(request: Request, token: str = Form(...)):
    print(f"Token recibido: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Token decodificado: {payload}")
        username: str = payload.get("sub")
        if username is None:
            print("Token inválido: 'sub' no encontrado")
            return templates.TemplateResponse(
                "enter_token.html",
                {"request": request, "error": "Token inválido: 'sub' no encontrado"},
                status_code=401
            )
        print(f"Token válido, usuario: {username}")
    except JWTError as e:
        print(f"Error al decodificar el token: {e}")
        return templates.TemplateResponse(
            "enter_token.html",
            {"request": request, "error": f"Token inválido: {str(e)}"},
            status_code=401
        )

    # Redirigir a /productos/filtrar sin pasar el token como parámetro de consulta
    print("Redirigiendo a /productos/filtrar")
    response = RedirectResponse(url="/productos/filtrar", status_code=303)
    # Actualizar la cookie con el token verificado
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Cambia a True si usas HTTPS
        samesite="lax",
        path="/",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Expiración en segundos
    )
    print("Redirección enviada con cookie actualizada")
    return response

# Mostrar formulario de registro
@router.get("/register")
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Procesar registro de nuevo usuario
@router.post("/register")
async def register(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        await register_user(form_data.username, form_data.password)
        # Para navegadores: redirigir al login
        if "text/html" in request.headers.get("accept", ""):
            return RedirectResponse(url="/auth/login", status_code=303)
        # Para clientes API: devolver un mensaje de éxito
        else:
            return JSONResponse(content={"message": "Usuario registrado exitosamente"})
    except HTTPException as e:
        if "text/html" in request.headers.get("accept", ""):
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": e.detail},
                status_code=e.status_code
            )
        else:
            raise e

# Cerrar sesión
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response