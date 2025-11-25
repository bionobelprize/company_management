"""MongoDB database connection and utilities."""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from .config import MONGODB_URL, DATABASE_NAME


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None


db = Database()


async def connect_to_mongo():
    """Create database connection."""
    db.client = AsyncIOMotorClient(MONGODB_URL)
    db.db = db.client[DATABASE_NAME]
    print(f"Connected to MongoDB: {DATABASE_NAME}")


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")


def get_database():
    """Get database instance."""
    return db.db
