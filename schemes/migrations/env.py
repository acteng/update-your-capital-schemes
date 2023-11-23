from alembic import context, command
from sqlalchemy import MetaData, create_engine

from schemes.authorities import add_tables as authorities_add_tables
from schemes.schemes.services import add_tables as schemes_add_tables
from schemes.users import add_tables as users_add_tables


metadata = MetaData()
schemes_add_tables(metadata)
authorities_add_tables(metadata)
users_add_tables(metadata)

connection = context.config.attributes.get("connection")

if not connection:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    connection = engine.connect()

context.configure(connection=connection, target_metadata=metadata)

with context.begin_transaction():
    context.run_migrations()

connection.close()
