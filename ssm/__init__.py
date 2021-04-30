from logging import getLogger

import configparser
import os

from halo import Halo
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ssm.modules.create_logger import EasyLogger

Base = declarative_base()

tmp_logger = getLogger('ssm')
tmp_logger = EasyLogger(tmp_logger, logger_level='DEBUG').create()

if os.path.exists('.env') is True:
    load_dotenv('.env')
else:
    tmp_logger.error('.envが存在しません')

config_ini = configparser.ConfigParser(os.environ)
config_ini.read('./config.ini', encoding='utf-8')

db_user = config_ini['DATABASE']['User']
db_port = config_ini['DATABASE']['Port']
db_host = config_ini['DATABASE']['Host']
db_password = config_ini['DATABASE']['Password']
db_default_database = config_ini['DATABASE']['Default_Database']

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_default_database}', echo=False)  # DEBUG時はTrueに

Session = sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)

session = Session()

spinner = Halo(text='Loading Now',
               spinner={
                   'interval': 300,
                   'frames': ['-', '+', 'o', '+', '-']
               })
