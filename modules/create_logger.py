import coloredlogs
from logging import getLogger, StreamHandler, DEBUG, Formatter, addLevelName

"""create easy logger"""

class easy_logger:
    def create(self, logger):
        """create logger"""
        # loggerのログレベル設定(ハンドラに渡すエラーメッセージのレベル)
        logger.setLevel(DEBUG)

        # --------------------------------
        # 2.handlerの設定
        # --------------------------------
        # handlerの生成
        stream_handler = StreamHandler()

        # handlerのログレベル設定(ハンドラが出力するエラーメッセージのレベル)
        stream_handler.setLevel(DEBUG)

        # --------------------------------
        # 3.loggerにhandlerをセット
        # --------------------------------
        logger.addHandler(stream_handler)
        logger.propagate = False

        coloredlogs.CAN_USE_BOLD_FONT = True
        coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'},
                                            'hostname': {'color': 'magenta'},
                                            'levelname': {'color': 'black', 'bold': True},
                                            'name': {'color': 'blue'},
                                            'programname': {'color': 'cyan'}
                                            }
        coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'color': 'red', 'bold': True},
                                            'error': {'color': 'red'},
                                            'warning': {'color': 'yellow'},
                                            'notice': {'color': 'magenta'},
                                            'info': {'color': 'green'},
                                            'debug': {},
                                            'spam': {'color': 'green', 'faint': True},
                                            'success': {'color': 'green', 'bold': True},
                                            'verbose': {'color': 'blue'}
                                            }

        coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

        # SUCCESSを追加
        logger.SUCCESS = 25 # WARNINGとINFOの間
        addLevelName(logger.SUCCESS, 'SUCCESS')
        setattr(logger, 'success', lambda message, *args: logger._log(logger.SUCCESS, message, args))
        return logger
easy_logger = easy_logger()