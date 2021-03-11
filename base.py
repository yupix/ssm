from logging import getLogger

from modules.create_logger import EasyLogger
from modules.db_manager import DbManager
from settings import session

# --------------------------------
# 1.loggerの設定
# --------------------------------
# loggerオブジェクトの宣言
logger = getLogger(__name__)

logger = EasyLogger(logger).create()

db_manager = DbManager(session=session, logger=logger, logger_level='debug')
