import logging
import requests

from thonk.service import Provider, Service

log = logging.getLogger(__name__)

class HttpServiceDiscovery(Provider):
	"""
	Discovers services by polling a HTTP endpoint and expecting JSON data back.

	The JSON format expected is as follows:

		{
			"services": [{
				"name": "My Cool Service",
				"host": "192.168.0.10",
				"port": 8080,
				"protocol": "tcp"
			}]
		}

	The "protocol" key may be emitted and defaults to "tcp".
	Other than that, all keys are required.

	:param url: Fully qualified URL to fetch data from
	"""
	def __init__(self, url: str):
		self.url = url
		self.session = requests.Session()
		self.active_rules = []

	def update(self):
		rules = []

		r = self.session.get(self.url)

		if r.ok:
			data = r.json()

			for srv_info in data["services"]:
				srv = Service(srv_info["name"],
							  srv_info["host"],
							  srv_info["port"],
							  srv_info.get("protocol", "tcp"))
				rules.append(srv)

		log.debug(f"HTTP service discovery: received {len(rules)} rules")
		self.active_rules = rules
		return rules

	def get_active_rules(self):
		return self.active_rules

provider_cls = HttpServiceDiscovery
