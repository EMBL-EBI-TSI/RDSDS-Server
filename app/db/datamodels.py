import sqlalchemy
from app.core.config import DATABASE_URL

metadata = sqlalchemy.MetaData()

objects = sqlalchemy.Table(
    "objects",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("self_uri", sqlalchemy.String),
    sqlalchemy.Column("size", sqlalchemy.BigInteger),
    sqlalchemy.Column("created_time", sqlalchemy.DateTime),
    sqlalchemy.Column("updated_time", sqlalchemy.DateTime),
    sqlalchemy.Column("version", sqlalchemy.String),
    sqlalchemy.Column("mime_type", sqlalchemy.String),
    sqlalchemy.Column("aliases", sqlalchemy.String),
)

checksums = sqlalchemy.Table(
    "checksums",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("checksum", sqlalchemy.String),
)

access_methods = sqlalchemy.Table(
    "access_methods",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("access_url", sqlalchemy.String),
    sqlalchemy.Column("region", sqlalchemy.String),
    sqlalchemy.Column("headers", sqlalchemy.String),
    sqlalchemy.Column("access_id", sqlalchemy.String),
)

contents = sqlalchemy.Table(
    "contents",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String),
    sqlalchemy.Column("id", sqlalchemy.String),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("drs_uri", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)

metadata.create_all(engine)

