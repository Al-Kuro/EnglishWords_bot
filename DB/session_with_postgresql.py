from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from DB.tables_postgresql import Base
import json


def get_settings_postgresql():
    with open('DB/settings.txt', 'r') as file_settings:
        settings = json.load(file_settings)

    return settings


def get_engine(settings):
    user = settings['pguser']
    passwd = settings['pgpasswd']
    host = settings['pghost']
    port = settings['pgport']
    db = settings['pgdb']

    url = f'postgresql://{user}:{passwd}@{host}:{port}/{db}'
    if not database_exists(url):
        create_database(url)
    cr_engine = create_engine(url, echo=False)

    return cr_engine


def get_engine_from_settings():
    settings = get_settings_postgresql()
    keys = ['pguser', 'pgpasswd', 'pghost', 'pgport', 'pgdb']
    if not all(key in keys for key in settings.keys()):
        raise Exception('Bad settings file ...')

    return get_engine(settings)


def get_session():
    cr_engine = get_engine_from_settings()
    Base.metadata.create_all(cr_engine)
    cr_session = sessionmaker(bind=cr_engine)()

    return cr_session
