import os
from distutils.util import strtobool
from logging import getLogger

import configparser

from halo import Halo

from ssm import session
from ssm.modules.create_logger import EasyLogger
from dbmanager import DbManager

config_ini = configparser.ConfigParser(os.environ)
config_ini.read('./config.ini', encoding='utf-8')
logger_level = config_ini['DEFAULT']['log']
use_language = config_ini['DEFAULT']['lang']
show_commit_log = config_ini['OPTIONS']['show_commit_log']
force_show_commit_log = config_ini['OPTIONS']['force_show_commit_log']

# --------------------------------
# 1.loggerの設定
# --------------------------------
# loggerオブジェクトの宣言
logger = getLogger('main')
logger = EasyLogger(logger, logger_level=f'{logger_level}').create()
spinner = Halo(text='初期化に成功しました', spinner='dots')
spinner.start()
db_manager = DbManager(session=session, logger=logger, logger_level=f'{logger_level}', show_commit_log=bool(strtobool(show_commit_log)), force_show_commit_log=bool(strtobool(force_show_commit_log)))
spinner.succeed()
