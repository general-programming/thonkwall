import iptc

from thonk.service import Service
from typing import List

__all__ = ["service_to_rule"]

def service_to_rule(service: Service) -> iptc.Rule:
	rule = iptc.Rule()
	rule.protocol = service.protocol

	tgt = rule.create_target("DNAT")
	tgt.to_destination = f"{service.host}:{service.port_range}"

	m = rule.create_match(service.protocol)
	m.dport = service.port_range

	return rule

def chain_has_rule(chain: iptc.Chain, test_rule: iptc.Rule):
	return any(map(lambda r: r == test_rule, chain.rules))

CHAIN_NAME = "thonkwall"
	
class IpTablesConsumer:
	def __init__(self, in_interface: str=None, dst_addr: str=None):
		self.table = iptc.Table(iptc.Table.NAT)
		self.chain = iptc.Chain(self.table, CHAIN_NAME)

		self.rule_in_interface = in_interface
 		self.rule_dst_addr = dst_addr

		if not self.table.is_chain(self.chain):
			self.table.create_chain(self.chain)

	def check(self):
		pre = iptc.Chain(self.table, "PREROUTING")
		jmp_rule = iptc.Rule()
		jmp_rule.create_target("thonkwall")

		if self.rule_in_interface:
			jmp_rule.in_interface = self.rule_in_interface
		if self.rule_dst_addr:
			jmp_rule.dst = self.rule_dst_addr

		if not chain_has_rule(pre, jmp_rule):
			pre.append_rule(jmp_rule)

	def update_rules(self, services: List[Service]):
		self.table.refresh()
		
		new_rules = map(service_to_rule, services)
		old_rules = self.chain.rules

		to_delete = [rule for rule in old_rules if rule not in new_rules]
		to_add = [rule for rule in new_rules if rule not in old_rules]

		print(f"+{len(to_add)} new rules, -{len(to_delete)} old rules")

		for r in to_delete:
			self.chain.delete_rule(r)

		for r in to_add:
			self.chain.append_rule(r)
