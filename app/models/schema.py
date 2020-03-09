from app.core.config import DATABASE_URL_STR
import sqlalchemy

engine = sqlalchemy.create_engine(
    DATABASE_URL_STR
)

connection = engine.connect()

metadata = sqlalchemy.MetaData()

objects = sqlalchemy.Table(
    "objects",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("self_uri", sqlalchemy.String),
    sqlalchemy.Column("size", sqlalchemy.BigInteger),
    sqlalchemy.Column("created_time", sqlalchemy.DateTime),
    sqlalchemy.Column("updated_time", sqlalchemy.DateTime),
)

checksums = sqlalchemy.Table(
    "checksums",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String, sqlalchemy.ForeignKey("objects.id")),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("checksum", sqlalchemy.String),
    
    sqlalchemy.UniqueConstraint('object_id', 'type', 'checksum', name='unique_checksum')
)

access_methods = sqlalchemy.Table(
    "access_methods",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String, sqlalchemy.ForeignKey("objects.id")),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("access_url", sqlalchemy.String),
    sqlalchemy.Column("region", sqlalchemy.String),
    sqlalchemy.Column("headers", sqlalchemy.String),
    sqlalchemy.Column("access_id", sqlalchemy.String),
)

contents = sqlalchemy.Table(
    "contents",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String, sqlalchemy.ForeignKey("objects.id")),
    sqlalchemy.Column("id", sqlalchemy.String),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("drs_uri", sqlalchemy.String),
)

datasets = sqlalchemy.Table(
    "datasets",
    metadata,
    sqlalchemy.Column("object_id", sqlalchemy.String, sqlalchemy.ForeignKey("objects.id")),
    sqlalchemy.Column("dataset", sqlalchemy.String),
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("mime_type", sqlalchemy.String),
    sqlalchemy.Column("bundle", sqlalchemy.String),
    sqlalchemy.Column("version", sqlalchemy.Integer),
    sqlalchemy.Column("created_time", sqlalchemy.DateTime),
    sqlalchemy.Column("aliases", sqlalchemy.String),
    
    sqlalchemy.UniqueConstraint('object_id', 'dataset', 'bundle', 'version', name='unique_datasets')
)

metadata.create_all(engine)

