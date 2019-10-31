from databases import Database


class DataBase:
    database: Database = None


db = DataBase()


async def get_database():
    return db.database
