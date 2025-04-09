from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
import bcrypt
from typing import Optional
from dotenv import load_dotenv
import os
from db.database import database

# Cargar variables de entorno
load_dotenv()

# Configuración del JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("La variable de entorno SECRET_KEY no está definida")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "2"))

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Función para obtener un usuario desde MongoDB
async def get_user(username: str):
    try:
        print(f"Buscando usuario: {username}")
        users_collection = database.get_collection("users")
        user = await users_collection.find_one({"username": username})
        if user:
            print(f"Usuario encontrado: {user['username']}")
            user["_id"] = str(user["_id"])
            return user
        print("Usuario no encontrado en la base de datos")
        return None
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos")

# Función para verificar contraseñas
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        print(f"Verificando contraseña: {plain_password} contra hash: {hashed_password}")
        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        print(f"Resultado de la verificación: {result}")
        return result
    except Exception as e:
        print(f"Error al verificar contraseña: {e}")
        return False

# Función para generar un token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para verificar el token y obtener el usuario actual
async def get_current_user(request: Request):
    print("=== Iniciando verificación de token en get_current_user ===")
    print(f"URL solicitada: {request.url}")
    print(f"Encabezados de la solicitud: {request.headers}")
    print(f"Cookies de la solicitud: {request.cookies}")

    # Obtener el token de la cookie
    token = request.cookies.get("access_token")
    print(f"Token encontrado en cookie: {token}")

    if not token:
        print("No se proporcionó un token en la cookie")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se proporcionó un token")

    print(f"Token que se va a decodificar: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Token decodificado en get_current_user: {payload}")
        username: str = payload.get("sub")
        if username is None:
            print("Token inválido: 'sub' no encontrado")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido: 'sub' no encontrado")
        print(f"Usuario extraído del token: {username}")
    except JWTError as e:
        print(f"Error al decodificar el token en get_current_user: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {str(e)}")

    user = await get_user(username)
    if user is None:
        print(f"Usuario {username} no encontrado en la base de datos")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    print("Autenticación exitosa en get_current_user")
    return user

# Función para registrar un nuevo usuario en MongoDB
async def register_user(username: str, password: str):
    try:
        users_collection = database.get_collection("users")
        
        # Verificar si el usuario ya existe
        existing_user = await users_collection.find_one({"username": username})
        if existing_user:
            raise HTTPException(status_code=400, detail="El usuario ya existe")

        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Crear el nuevo usuario
        new_user = {
            "username": username,
            "hashed_password": hashed_password
        }
        
        # Insertar el usuario en la base de datos
        result = await users_collection.insert_one(new_user)
        return {"id": str(result.inserted_id), "username": username}
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al registrar usuario en la base de datos")