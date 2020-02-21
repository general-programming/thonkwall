from configparser import ConfigParser

import importlib

def get_providers(settings_path: str):
	settings = ConfigParser()
	settings.read(settings_path)

	providers = settings.sections()

	for provider in providers:
		try:
			mod = importlib.import_module(provider)
			kwargs = settings[provider]

			yield mod.provider_cls(**kwargs)
		except ModuleNotFoundError:
			print(f"Could not import provider '{provider}', does it exist?")
