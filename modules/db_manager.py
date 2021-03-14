from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import DetachedInstanceError


class DbManager:
	def __init__(self, session=None, logger=None, logger_level: str = None, show_commit_log: bool = False, force_show_commit_log:bool = False):
		self.session = session
		self.logger = logger
		self.logger_level = logger_level
		self.show_commit_log = show_commit_log
		self.force_show_commit_log = force_show_commit_log

	async def check_logger(self, message: str = None, logger_level: str = None, show_commit_log: bool=False):
		"""ログの出力のレベル分けを行い適切に出力します"""
		if show_commit_log is True or self.force_show_commit_log is True and self.logger is not None:
			if logger_level == 'debug':
				self.logger.debug(message)
			elif logger_level == 'error':
				self.logger.error(message)
			elif logger_level == 'warn':
				self.logger.warn(message)
			elif logger_level == 'info':
				self.logger.info(message)

	async def commit(self, content, autoincrement=None, commit_type: str = 'insert', result_type: str = 'content', show_commit_log: bool = False):
		"""データをコミットします"""
		if self.force_show_commit_log is False and show_commit_log is not False:
			show_commit_log = self.show_commit_log
		elif self.force_show_commit_log is True:
			show_commit_log = True
		if commit_type == 'insert':
			self.session.add(content)
		try:
			self.session.commit()
			await self.check_logger('commitに成功しました', f'debug', show_commit_log)
			if autoincrement is None:
				if result_type == 'content':
					result = content

			elif autoincrement is True:
				result = content.id

		except IntegrityError:
			self.session.rollback()
			result = 'IntegrityError'
			await self.check_logger('commitを行う際に重複が発生しました', f'warn', show_commit_log)
		return result


if __name__ == "__main__":
	DbManager()
