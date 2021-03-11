from sqlalchemy.exc import IntegrityError


class DbManager:
	def __init__(self, session=None, logger=None, logger_level: str = None):
		self.session = session
		self.logger = logger
		self.logger_level = logger_level

	async def check_logger(self, message: str = None, logger_level: str = None):
		if self.logger is not None:
			if logger_level == 'debug' and self.logger_level == 'debug':
				self.logger.debug(message)
			if logger_level == 'info':
				self.logger.info(message)

	async def db_commit(self, content, autoincrement=None, commit_type='insert', result_type='content'):
		if commit_type == 'insert':
			self.session.add(content)
		try:
			self.session.commit()
			await self.check_logger('commitに成功しました', f'debug')
			if autoincrement is None:
				if result_type == 'content':
					result = content

			elif autoincrement is True:
				result = content.id

		except IntegrityError as e:
			self.session.rollback()
			result = 'IntegrityError'
			await self.check_logger('commitを行う際に重複が発生しました', f'debug')
		finally:
			self.session.close()
		return result


if __name__ == "__main__":
	DbManager()
