import databases.Database

class DataBase:
    db: Database = None


db = DataBase()


async def get_database():
    return db
