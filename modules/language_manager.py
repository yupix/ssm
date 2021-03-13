import json


class LanguageManager:
	def __init__(self, base_path=None, lang=None, module_name=None):
		self.base_path = base_path
		self.lang = lang
		self.module_name = module_name

	def get(self):
		with open(f'{self.base_path}{self.lang}/{self.module_name}.json') as f:
			get_language = json.load(f)
			return get_language
