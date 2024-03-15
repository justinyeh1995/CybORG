import collections
from pprint import pprint
import re
import traceback 
from typing import List, Dict
from CybORG.Tutorial.Mininet.utils.util import set_name_map, parse_mininet_ip, \
                            build_mininet_host_to_cyborg_ip_map, build_cyborg_ip_to_mininet_host_map

class CybORGMininetMapper:
    def __init__(self):
        # Inner CybORG lookup
        self.ip_map = {}
        self.cidr_map = {}
        self.cyborg_ip_to_host_map = {}
        self.cyborg_host_to_ip_map = {}

        # Inner Mininet lookup
        self.mininet_host_to_ip_map = {}
        self.mininet_ip_to_host_map = {}

        # CybORG<->Mininet lookup
        self.cyborg_to_mininet_name_map = {}
        self.mininet_host_to_cyborg_ip_map = {}
        self.cyborg_ip_to_mininet_host_map = {}
        self.cyborg_to_mininet_host_map = {}
        self.mininet_to_cyborg_host_map = {}
        self.cyborg_ip_to_mininet_ip_map = {}
        self.mininet_ip_to_cyborg_ip_map = {}
        
    def init_mapping(self, cyborg) -> None: 
        self.ip_map = cyborg.get_ip_map()
        self.cidr_map = cyborg.get_cidr_map()
        self.cyborg_ip_to_host_map = {str(ip): host for host, ip in self.ip_map.items()}
        self.cyborg_host_to_ip_map = {host: str(ip) for host, ip in self.ip_map.items()}
        
        self.cyborg_to_mininet_name_map = set_name_map(cyborg)

    
    def update_mapping(self, output: str, topology_data: dict) -> None:
        
        matches = parse_mininet_ip(output)

        # Create a dictionary to map host names to their IP addresses
        self.mininet_host_to_ip_map = {match.group('host'): match.group('ip') for match in matches}

        self.mininet_ip_to_host_map = {match.group('ip'): match.group('host') for match in matches}

        self.mininet_host_to_cyborg_ip_map = build_mininet_host_to_cyborg_ip_map(topology_data) 

        self.cyborg_ip_to_mininet_host_map = build_cyborg_ip_to_mininet_host_map(topology_data)

        self.cyborg_to_mininet_host_map = { 
            self.cyborg_ip_to_host_map[cyborg_ip]:self.cyborg_ip_to_mininet_host_map[cyborg_ip] 
            for cyborg_ip in self.cyborg_ip_to_host_map}

        self.mininet_to_cyborg_host_map = {
            self.cyborg_ip_to_mininet_host_map[cyborg_ip]:self.cyborg_ip_to_host_map[cyborg_ip] 
            for cyborg_ip in self.cyborg_ip_to_host_map}
        
        self.cyborg_ip_to_mininet_ip_map = { 
            self.cyborg_host_to_ip_map[cyborg_h]:self.mininet_host_to_ip_map[mininet_h] 
                for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()}
        
        self.mininet_ip_to_cyborg_ip_map = {
            self.mininet_host_to_ip_map[mininet_h]:self.cyborg_host_to_ip_map[cyborg_h] 
                for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()}

    
    def __str__(self):
        # For a more user-friendly representation
        return (f"CybORGMininetMapper:\n"
                f"  CybORG IP -> Host Mapping: {len(self.cyborg_ip_to_host_map)} items\n"
                f"  Mininet Host -> IP Mapping: {len(self.mininet_host_to_ip_map)} items\n"
                f"  CybORG to Mininet Name Mapping: {len(self.cyborg_to_mininet_name_map)} items\n"
                f"  Mininet Host to CybORG IP Mapping: {len(self.mininet_host_to_cyborg_ip_map)} items\n"
                f"  CybORG IP to Mininet Host Mapping: {len(self.cyborg_ip_to_mininet_host_map)} items\n"
                f"  CybORG to Mininet Host Mapping: {len(self.cyborg_to_mininet_host_map)} items\n"
                f"  Mininet to CybORG Host Mapping: {len(self.mininet_to_cyborg_host_map)} items\n"
                f"  CybORG IP to Mininet IP Mapping: {len(self.cyborg_ip_to_mininet_ip_map)} items\n"
                f"  Mininet IP to CybORG IP Mapping: {len(self.mininet_ip_to_cyborg_ip_map)} items")

    
    def __repr__(self):
        # For a more detailed, developer-focused representation
        return (f"CybORGMininetMapper(\n"
        f"  ip_map={self.ip_map},\n"
        f"  cidr_map={self.cidr_map},\n"
        f"  cyborg_ip_to_host_map={self.cyborg_ip_to_host_map},\n"
        f"  cyborg_host_to_ip_map={self.cyborg_host_to_ip_map},\n"
        f"  mininet_host_to_ip_map={self.mininet_host_to_ip_map},\n"
        f"  mininet_ip_to_host_map={self.mininet_ip_to_host_map},\n"
        f"  cyborg_to_mininet_name_map={self.cyborg_to_mininet_name_map},\n"
        f"  mininet_host_to_cyborg_ip_map={self.mininet_host_to_cyborg_ip_map},\n"
        f"  cyborg_ip_to_mininet_host_map={self.cyborg_ip_to_mininet_host_map},\n"
        f"  cyborg_to_mininet_host_map={self.cyborg_to_mininet_host_map},\n"
        f"  mininet_to_cyborg_host_map={self.mininet_to_cyborg_host_map},\n"
        f"  cyborg_ip_to_mininet_ip_map={self.cyborg_ip_to_mininet_ip_map},\n"
        f"  mininet_ip_to_cyborg_ip_map={self.mininet_ip_to_cyborg_ip_map}\n"
        f")")
