import yaml
import traceback 
from typing import Dict, List

from CybORG.Tutorial.Mininet.utils.util import get_routers_info, get_lans_info, get_links_info, get_nats_info, \
                                                generate_routing_rules

class YamlTopologyManager:
    def __init__(self, topology_data: Dict = None):
        self.topology_data = topology_data or {'topo': {'routers': [], 'lans': [], 'links': [], 'routes': [], 'nats': []}}
        

    def generate_topology_data(self, cyborg, cyborg_to_mininet_name_map) -> None:
        """ 
        Write the topo into a yaml file
        """
        try:
            # Structure the 'Routers' information
            self.topology_data['topo']['routers'] = get_routers_info(cyborg, cyborg_to_mininet_name_map)
    
            # Structure the 'LANs' information
            self.topology_data['topo']['lans'] = get_lans_info(cyborg, cyborg_to_mininet_name_map)
    
            # Structure the 'Links' information
            self.topology_data['topo']['links'] = get_links_info(cyborg, cyborg_to_mininet_name_map)

            # self.topology_data['topo']['nats'] = get_nats_info(cyborg, self.topology_data)

            self.topology_data['topo']['routes'] = generate_routing_rules(self.topology_data)

            print("Topology for file 'network_topology.yaml' created.")
                    
        except Exception as e:
            print("An error occurred while creating the topology:")
            print(e)
            traceback.print_exc() 

    
    def save_topology(self, file_path: str) -> None:
        try:     
            with open(file_path, 'w') as file:
                yaml.dump(self.topology_data, file, default_flow_style=False, sort_keys=False)
    
            print("YAML file 'network_topology.yaml' created.")
                 
        except Exception as e:
            print("An error occurred while creating the YAML file:")
            print(e)
            traceback.print_exc()    


    def get_topology(self) -> Dict:
        return self.topology_data
