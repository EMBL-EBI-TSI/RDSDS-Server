import logging
import databases

from app.core.config import DATABASE_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT
from .database import db


async def connect_to_postgres():
    logging.info("Connecting to database")
    db.database = databases.Database(DATABASE_URL, min_size=MIN_CONNECTIONS_COUNT, max_size=MAX_CONNECTIONS_COUNT )
    await db.database.connect()
    
    logging.info("Connected to database")


async def close_postgres_connection():
    logging.info("Closing connection")

    await db.database.disconnect()

    logging.info("Connection closed")
