# db/database.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la conexión a MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://samuel:admin123@cluster0.w02dh.mongodb.net/umb-practica")
client = AsyncIOMotorClient(MONGODB_URL)
database = client.get_database("umb-practica")

def get_collection(collection_name: str):
    return database.get_collection(collection_name)