import consulate

from thonk.service import Provider, Service

__all__ = ["ConsulServiceDiscovery"]

def _tag_value(val: str):
	ci_val = val.lower()
	
	if ci_val in ["true", "yes", "y"]:
		return True
	elif ci_val in ["false", "no", "n"]:
		return False
	elif val == "":
		return None

	try:
		return int(val)
	except ValueError:
		pass

	return val

class ConsulServiceDiscovery(Provider):
	def __init__(self, host: str, port: int=8500):
		self.consul = consulate.Consul(host=host, port=port)
		self.active_rules = []

	def _parse_tag(self, tag: str):
		if not tag.startswith("thonkwall"):
			return None

		parts = tag.split("=")
		if len(parts) == 1:
			return parts[0], True
		elif len(parts) == 2:
			return parts[0], _tag_value(parts[1])
		else:
			return None

	def _parse_tags(self, tag_list):
		tags = {}
		
		for tag in tag_list:
			result = self._parse_tag(tag)

			if result is not None:
				tags[result[0]] = result[1]
				
		return tags
	
	def update(self):
		rules = []
		services = self.consul.catalog.services()[0]

		for sid, taglist in services.items():
			tags = self._parse_tags(taglist)

			if not tags.get("thonkwall.enable", False):
				continue

			service = self.consul.catalog.service(sid)[0]

			name = service["ServiceName"] or sid
			host = tags.get("thonkwall.host", service["ServiceAddress"] or service["Address"])
			port = tags.get("thonkwall.port", service["ServicePort"])
			protocol = tags.get("thonkwall.protocol", "tcp")
			
			local_service = Service(name, host, int(port), protocol)
			rules.append(local_service)

		print(f"Consul discovery: found {len(rules)} rules")
		self.active_rules = rules
		return rules
	
	def get_active_rules(self):
		return self.active_rules

provider_cls = ConsulServiceDiscovery
