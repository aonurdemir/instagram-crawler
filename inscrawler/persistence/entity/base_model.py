from peewee import PostgresqlDatabase, Model

from inscrawler.persistence.database.config import config

config = config()
psql_db = PostgresqlDatabase(config['database'], user=config['user'], password=config['password'], host=config['host'])


class BaseModel(Model):
    class Meta:
        database = psql_db
