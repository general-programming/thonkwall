# thonkwall

a firewall management system with service discovery

thonkwall is a firewall management daemon which looks for configuration
from several providers (consul, file, etc.) and creates DNAT rules, to
allow for dynamic port forwarding configuration.
