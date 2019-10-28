import logging
import databases

from app.core.config import DATABASE_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT
from .database import db


async def connect_to_postgres():
    logging.info("Connecting to database")

    db = databases.Database(DATABASE_URL.replace("postgres://","postgresql://"), min_size=MIN_CONNECTIONS_COUNT, max_size=MAX_CONNECTIONS_COUNT )
    await db.connect()
    
    logging.info("Connected to database")


async def close_postgres_connection():
    logging.info("Closing connection")

    await db.disconnect()

    logging.info("Connection closed")
