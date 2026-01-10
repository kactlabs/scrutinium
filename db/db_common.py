"""
Common database utility functions
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

def get_database():
    """Get database instance"""
    return db

def get_collection(collection_name: str):
    """Get collection instance"""
    return db[collection_name]