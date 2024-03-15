import re
import traceback 
from pprint import pprint
from typing import List, Dict

def parse_nmap_network_scan(nmap_output, target, mapper) -> List:
    res = {'success': True}
    subnet = target
    mininet_ip_addresses = re.findall(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', nmap_output)
    cyborg_ip_addresses = [mapper.mininet_ip_to_cyborg_ip_map[ip] for ip in mininet_ip_addresses if ip in mapper.mininet_ip_to_cyborg_ip_map]
    res[subnet] = cyborg_ip_addresses
    return res
    
def parse_nmap_port_scan(nmap_output, target, mapper) -> List:
    res = {'success': True}
    mininet_host = target
    ip = mapper.mininet_host_to_cyborg_ip_map[mininet_host]
    # Regular expression to match the port information
    port_info_regex = re.compile(r'(\d+)/(\w+)\s+open\s+(\w+)\s+(.+)')
    
    # Find all matches
    matches = port_info_regex.findall(nmap_output)
    
    # Process matches
    ports = []
    for match in matches:
        port_number, protocol, service_name, version = match
        ports.append({
            'port': port_number,
            'protocol': protocol,
            'service': service_name,
            'version': version.strip()
        })    
    res[ip] = ports    
    return res
    
class ResultsBundler:
    def bundle(self, target, cyborg_action, isSuccess, mininet_cli_str, mapper) -> Dict:
        # @To-Do
        print(isSuccess)
        if not isSuccess:
            return {'success': False}
        
        if cyborg_action == "DiscoverRemoteSystems":
            return parse_nmap_network_scan(mininet_cli_str, target, mapper)
            
        elif cyborg_action == "DiscoverNetworkServices":
            return parse_nmap_port_scan(mininet_cli_str, target, mapper)

        return {'success': True}
        