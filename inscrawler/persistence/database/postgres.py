import psycopg2
from .config import config


def connect():
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        print('Successfully connected')
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return None
