import subprocess
import pexpect
import yaml
import collections
from pprint import pprint
import re
import traceback 
from typing import List, Dict
from ipaddress import IPv4Address, IPv4Network
from Mininet.mininet_utils.custom_utils import IP_components
from Mininet.utils.util import parse_action, parse_mininet_ip, \
                            set_name_map, get_routers_info, get_lans_info, \
                            get_links_info, get_nats_info, \
                            build_mininet_host_to_cyborg_ip_map, build_cyborg_ip_to_mininet_host_map, \
                            generate_routing_rules, \
                            translate_discover_remote_systems, \
                            translate_discover_network_services, \
                            translate_exploit_network_services, \
                            translate_restore, translate_remove 
                       

class MininetAdapter:
    def __init__(self):
        
        self.cyborg = None
        self.ip_map = None
        self.cidr_map = None
        
        self.cyborg_ip_to_host_map = None
        self.cyborg_host_to_ip_map = None

        self.mininet_host_to_ip_map = None
        self.mininet_ip_to_host_map = None
         
        self.cyborg_to_mininet_host_map = None
        self.mininet_to_cyborg_host_map = None
        
        self.cyborg_to_mininet_name_map = None
                
        self.topology_data = None
        
        self.mininet_process = None


    def __repr__(self) -> str:
        # Utilize pprint for prettier printing of dictionaries
        pp = pprint.PrettyPrinter(indent=4)
        return f"MininetAdapter(\n" \
               f"cyborg={self.cyborg},\n" \
               f"ip_map={pp.pformat(self.ip_map)},\n" \
               f"cidr_map={pp.pformat(self.cidr_map)},\n" \
               f"cyborg_to_mininet_name_map={pp.pformat(self.cyborg_to_mininet_name_map)},\n" \
               f"cyborg_to_mininet_host_map={pp.pformat(self.cyborg_to_mininet_host_map)},\n" \
               f"cyborg_host_to_ip_map={pp.pformat(self.cyborg_host_to_ip_map)},\n" \
               f"mininet_host_to_ip_map={pp.pformat(self.mininet_host_to_ip_map)},\n" \
               f"mininet_ip_to_host_map={pp.pformat(self.mininet_ip_to_host_map)},\n" \
               f"mininet_process={'Running' if self.mininet_process else 'Not running'},\n" \
               f")"

    
    def set_environment(self, cyborg) -> None:
        self.cyborg = cyborg
        

    def create_mapping(self) -> None: 
        self.ip_map = self.cyborg.get_ip_map()
        self.cidr_map = self.cyborg.get_cidr_map()
        self.cyborg_ip_to_host_map = {str(ip): host for host, ip in self.ip_map.items()}
        self.cyborg_host_to_ip_map = {host: str(ip) for host, ip in self.ip_map.items()}
        
        self.cyborg_to_mininet_name_map = set_name_map(self.cyborg)


    def _create_yaml(self) -> None:
        """ 
        Write the topo into a yaml file
        """
        try:
            # Initialize topology data
            self.topology_data = {
                'topo': {
                    'routers': [],
                    'lans': [],
                    'links': [],  # Placeholder, add your actual links here
                    'routes': [],
                    'nats': []
                }
            }        
            
            # Structure the 'Routers' information
            self.topology_data['topo']['routers'] = get_routers_info(self.cyborg, self.cyborg_to_mininet_name_map)
    
            # Structure the 'LANs' information
            self.topology_data['topo']['lans'] = get_lans_info(self.cyborg, self.cyborg_to_mininet_name_map)
    
            # Structure the 'Links' information
            self.topology_data['topo']['links'] = get_links_info(self.cyborg, self.cyborg_to_mininet_name_map)

            self.topology_data['topo']['nats'] = get_nats_info(self.cyborg, self.topology_data)

            self.topology_data['topo']['routes'] = generate_routing_rules(self.topology_data)

            # pprint(self.topology_data)

            # Convert the data structure to YAML format
            yaml_content = yaml.dump(self.topology_data, default_flow_style=False, sort_keys=False)
            
            # Write the YAML content to a file
            with open('network_topology.yaml', 'w') as file:
                file.write(yaml_content)
            
            print("YAML file 'network_topology.yaml' created.")
            
        except Exception as e:
            print("An error occurred while creating the YAML file:")
            print(e)
            traceback.print_exc() 

        
    
    def update_mapping(self, output: str) -> None:
        
        matches = parse_mininet_ip(output)
        
        # Create a dictionary to map host names to their IP addresses
        self.mininet_host_to_ip_map = {match.group('host'): match.group('ip') for match in matches}

        self.mininet_ip_to_host_map = {match.group('ip'): match.group('host') for match in matches}

        self.mininet_host_to_cyborg_ip_map = build_mininet_host_to_cyborg_ip_map(self.topology_data) 

        self.cyborg_ip_to_mininet_host_map = build_cyborg_ip_to_mininet_host_map(self.topology_data)

        self.cyborg_to_mininet_host_map = { 
            self.cyborg_ip_to_host_map[cyborg_ip]:self.cyborg_ip_to_mininet_host_map[cyborg_ip] 
            for cyborg_ip in self.cyborg_ip_to_host_map}

        self.mininet_to_cyborg_host_map = {
            self.cyborg_ip_to_mininet_host_map[cyborg_ip]:self.cyborg_ip_to_host_map[cyborg_ip] 
            for cyborg_ip in self.cyborg_ip_to_host_map}
        
        self.cyborg_ip_to_mininet_ip_map = { 
            self.cyborg_host_to_ip_map[cyborg_h]:self.mininet_host_to_ip_map[mininet_h] 
                for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()}
        
        self.mininet_ip_to_cyborg_ip_map ={
            self.mininet_host_to_ip_map[mininet_h]:self.cyborg_host_to_ip_map[cyborg_h] 
                for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()}

        # pprint(self.cyborg_ip_to_mininet_host_map)
        # pprint(self.cyborg_ip_to_host_map)
        # pprint(self.mininet_host_to_ip_map)
        # pprint(self.cyborg_ip_to_mininet_ip_map)

    
    def create_mininet_topo(self) -> str:
        try:
            self._create_yaml()
            # Start the Mininet topology creation process with pexpect
            self.mininet_process = pexpect.spawn("sudo python3 Mininet/mininet_utils/custom_net.py -y network_topology.yaml")

            # Set a timeout for responses (adjust as needed)
            self.mininet_process.timeout = 300

            # Wait for the process to complete or for an expected output
            # You can adjust this depending on the expected output of your script
            self.mininet_process.expect("mininet>")

            # Print the output
            print("Mininet Topology Created Successfully:")
            output = self.mininet_process.before.decode()  # Decoding may be necessary
            # print(output)

            return output

        except Exception as e:
            # Handle exceptions
            print("An error occurred while creating Mininet topology:")
            print(str(e))
            traceback.print_exc() 
        
    
    def _parse_last_action(self, agent_type):
        action_str = self.cyborg.get_last_action(agent_type).__str__()
        
        target_host, action_type, isSucess = parse_action(self.cyborg, 
                                                action_str, 
                                                agent_type, 
                                                self.cyborg_ip_to_host_map)
        
        return self.cyborg_to_mininet_host_map.get(target_host, target_host), action_type, isSucess        
        
    
    def build_red_cmd(self, action_type, target_host) -> str:
        host = self.cyborg_to_mininet_host_map['User0'] # red host is always user0
        timeout = 60
        # @To-Do code smells
        if action_type == "DiscoverRemoteSystems":
            print("Red Discover Remote Systems")
            action = "nmap -sn"
            target = target_host
        elif action_type == "DiscoverNetworkServices":
            print("Red Discover Network Services")
            action = "nmap -sV"
            target = target_host
        elif action_type == "ExploitRemoteService":
            print("Red Exploit Network Services")
            action = "ssh cpswtjustin@"
            target = "8.8.8.8" # dummy
        elif action_type == "PrivilegeEscalate":
            action = "ping" # dummy
            target = "nat0" # dummy
        else:
            action = "sleep 1" # dummy
            target = "" # dummy
            
        cmd = f'{host} timeout {timeout} {action} {target}'
        
        return cmd


    def build_blue_cmd(self, action_type, target_host) -> str:
        timeout = 10
        # @To-Do code smells
        # blue host is undecided at the moment
        if action_type == "Remove":
            print("Blue Remove")
        elif action_type == "Restore":
            print("Blue Restore")
        elif action_type == "Monitor":
            print("Blue Monitor")
        host = ""
        action = ""
        cmd = f'{host} timeout {timeout} {action}'
        cmd = 'lan1h1 ping -c 1 lan1h2'
        return cmd


    def send_mininet_command(self, agent_type) -> str:
        try:
            if self.mininet_process and self.mininet_process.isalive():
                # translate the last action of an agent to Linux command?
                target_host, action_type, isSucess = self._parse_last_action(agent_type)
                print((agent_type, action_type, isSucess, target_host))
    
                command = self.build_red_cmd(action_type, target_host) if agent_type == "Red" \
                                                                       else self.build_blue_cmd(action_type, target_host)

                print(command)
                # Send the command to Mininet
                self.mininet_process.sendline(command)
    
                # Wait for the command to be processed and output to be generated
                # The specific pattern to expect might vary based on your command and Mininet's output
                self.mininet_process.expect('mininet>')
    
                # Retrieve and print the output of the command
                output = self.mininet_process.before.decode()
                
                return output

            else:
                print("Mininet process is not running. Please start the topology first.")
                return "Mininet process is not running. Please start the topology first."
                
        except Exception as e:
            # Handle exceptions
            print("An error occurred while sending command to Mininet topology:")
            print(str(e))
            traceback.print_exc() 


    
    def perform_emulation(self):
        for type in ['Blue', 'Red']:
            output = self.send_mininet_command(type)
            print(output)
            # @To-Do Parse the output from the command
    
    
    def clean(self) -> None:
        # First, ensure that the existing Mininet subprocess is terminated
        try:
            # First, check if a Mininet process is running and terminate it
            if self.mininet_process and self.mininet_process.isalive():
                self.mininet_process.terminate()
                self.mininet_process.expect(pexpect.EOF)  # Wait for termination
                print("Terminated the ongoing Mininet topology.")

            # Now, run the Mininet cleanup command
            cleanup_process = pexpect.spawn("sudo mn -c")
            cleanup_process.timeout = 60
            cleanup_process.expect(pexpect.EOF)  # Wait for the end of the process
            print("Cleaned up the topology successfully")
            # print(cleanup_process.before.decode())

        except Exception as e:
            print("An error occurred while cleaning up the topology:")
            print(str(e))

        finally:
            if cleanup_process is not None and cleanup_process.isalive():
                cleanup_process.terminate()

    
    def reset(self) -> None:
        self.clean()
        self.create_mapping()
        expect_str = self.create_mininet_topo()
        self.update_mapping(expect_str)


if __name__ == "__main__":
    print("Hello Mininet Adapter!")
    
        