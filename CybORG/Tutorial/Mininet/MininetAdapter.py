import subprocess
import pexpect
import yaml
import collections
from pprint import pprint
import re
import traceback 
from typing import List, Dict
from ipaddress import IPv4Address, IPv4Network
from CybORG.Tutorial.Mininet.mininet_utils.custom_utils import IP_components
from CybORG.Tutorial.Mininet.mininet_adapter import YamlTopologyManager, \
                                    MininetCommandInterface, \
                                    CybORGMininetMapper, \
                                    RedActionTranslator, BlueActionTranslator, \
                                    ResultsBundler
from CybORG.Tutorial.Mininet.utils.util import parse_action, parse_mininet_ip, \
                            set_name_map, get_routers_info, get_lans_info, get_links_info, \
                            translate_discover_remote_systems, \
                            translate_discover_network_services, \
                            translate_exploit_network_services, \
                            translate_restore, translate_remove 
                       

class MininetAdapter:
    def __init__(self):
        self.topology_manager = YamlTopologyManager()
        self.command_interface = MininetCommandInterface()
        self.mapper = CybORGMininetMapper()
        self.blue_action_translator = BlueActionTranslator()
        self.red_action_translator = RedActionTranslator()
        self.results_bundler = ResultsBundler()

    
    def set_environment(self, cyborg):
        # Setup based on cyborg environment...
        self.cyborg = cyborg

    
    def _parse_last_action(self, agent_type):
        action_str = self.cyborg.get_last_action(agent_type).__str__()
        
        target_host, action_type, isSuccess = parse_action(self.cyborg, 
                                                action_str, 
                                                agent_type, 
                                                self.mapper.cyborg_ip_to_host_map)
        
        return self.mapper.cyborg_to_mininet_host_map.get(target_host, target_host), action_type, isSuccess 
    
    
    def reset(self):
        self.clean()

        self.mapper.init_mapping(self.cyborg)

        # Create YAML topology file
        file_path = 'network_topology.yaml'
        # This involves updating topology data and mappings
        self.topology_manager.generate_topology_data(self.cyborg, self.mapper.cyborg_to_mininet_name_map)
        self.topology_manager.save_topology(file_path)
        
        # Start Mininet with the topology
        expect_text = self.command_interface.start_mininet(file_path)

        self.mapper.update_mapping(expect_text, self.topology_manager.topology_data)


    def perform_emulation(self) -> Dict:
        # Example of performing emulation
        # Translate CybORG action to Mininet command and send it
        # @To-Do
        obs = {}
        for type in ['Blue', 'Red']:
            cyborg_action, target, isSuccess = self._parse_last_action(type)
            
            if type == "Blue":
                mininet_command = self.blue_action_translator.translate(cyborg_action, 
                                                                    target, 
                                                                    self.mapper.cyborg_to_mininet_host_map)  
            else:
                mininet_command = self.red_action_translator.translate(cyborg_action, 
                                                                    target,
                                                                    self.mapper.cyborg_to_mininet_host_map)
                
            mininet_cli_text = self.command_interface.send_command(mininet_command) if isSuccess else "Unsuccessful Action"
            print(mininet_cli_text)
            mininet_obs = self.results_bundler.bundle(mininet_cli_text)
            obs[type] = mininet_obs
        return obs

    
    def clean(self):
        self.command_interface.clean()

if __name__ == "__main__":
    print("Hello Mininet Adapter!")

