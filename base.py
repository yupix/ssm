import os
from logging import getLogger

import configparser

from modules.create_logger import EasyLogger
from modules.db_manager import DbManager
from settings import session
config_ini = configparser.ConfigParser(os.environ)
config_ini.read('./config.ini', encoding='utf-8')
logger_level = config_ini['DEFAULT']['log']

# --------------------------------
# 1.loggerの設定
# --------------------------------
# loggerオブジェクトの宣言
logger = getLogger(__name__)
logger = EasyLogger(logger, logger_level=f'{logger_level}').create()

db_manager = DbManager(session=session, logger=logger, logger_level=f'{logger_level}')
