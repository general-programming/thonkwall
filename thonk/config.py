from configparser import ConfigParser

import importlib
import logging

log = logging.getLogger(__name__)

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
			log.warning(f"Could not import provider '{provider}', does it exist?")
		except AttributeError:
			log.warning(f"Module {provider} has no 'provider_cls' attribute, skipping")
