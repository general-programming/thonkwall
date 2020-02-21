from thonk.service import ProviderAggregator
from thonk.firewall import IpTablesConsumer
from thonk import config

import os
import sched
import logging

if __name__ == "__main__":
	log_level = os.getenv("THONKWALL_LOG_LEVEL", logging.INFO)
	logging.basicConfig(format="%(asctime)s [%(name)s %(levelname)s]: %(message)s", level=log_level)
		
	settings_path = os.getenv("THONKWALL_PROVIDERS", os.path.abspath("providers.ini"))

	in_interface = os.getenv("THONKWALL_RULE_IN_INTERFACE", None)
	dst_addr = os.getenv("THONKWALL_RULE_DST_ADDR", None)

	consumer = IpTablesConsumer(in_interface, dst_addr)
	consumer.check()
	
	providers = config.get_providers(settings_path)
	p = ProviderAggregator(*providers)

	logging.info(f"thonkwall starting, {len(p.providers)} providers")
	
	p.update()

	s = sched.scheduler()

	while True:
		consumer.update_rules(p.get_active_rules())
		
		for provider in p.providers:
			s.enter(30, 1, provider.update)

		try:
			s.run()
		except KeyboardInterrupt:
			break

	logging.info("Shutting down!")
