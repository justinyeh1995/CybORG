import subprocess
import inspect
import time
import os
from statistics import mean, stdev
import random
import collections
from pprint import pprint

class GameStateManager:
    def __init__(self):
        self.blue_agent = None
        self.red_agent = None
        self.cyborg = None
        self.num_steps = None
        self.ip_map = None
        self.host_map = None
        self.game_states = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(dict)))
        
        self.compromised_hosts = set()
        self.exploited_hosts = set()
        self.escalated_hosts = set()
        self.discovered_subnets = set()
        self.discovered_systems = set()

    def set_environment(self, cyborg=None, red_agent=None, blue_agent=None, num_steps=30):
        self.cyborg = cyborg
        self.blue_agent = blue_agent
        self.red_agent = red_agent
        self.num_steps= num_steps
        self._create_ip_host_maps()
        
    def _create_ip_host_maps(self):
        self.ip_map = dict(map(lambda item: (str(item[0]), item[1]), self.cyborg.environment_controller.state.ip_addresses.items()))
        self.host_map = {host: str(ip) for ip, host in self.ip_map.items()}

    def _get_node_color(self, node, discovered_subnets=None, discovered_systems=None, exploited_hosts=None, escalated_hosts=None):
        color = "green"
        
        if 'router' in node:
            if node in discovered_subnets:
                color = 'rosybrown'
        
        if node in discovered_systems:
            color = "lightgreen"
        
        if node in escalated_hosts:
            color = "red"
            
        elif node in exploited_hosts:
            color = "orange"
        
        return color

    def _get_node_border(self, node, target_host=None, reset_host=None):
        if node in target_host:
            border = dict(width=2, color='#99004C')
        elif node in reset_host:
            border = dict(width=2, color='blue')
        else:
            border = dict(width=0, color='white')
        return border
        
    def _parse_action(self, cyborg, action_str, agent, host_map, ip_map):
        action_type = action_str.split(" ")[0]
        target_host = ""
        if cyborg.get_observation(agent)['success'].__str__() == 'TRUE':
            target_host = action_str.split(" ")[-1]
            # Update target host if it's an IP address to get the hostname
            target_host = ip_map.get(target_host, target_host)
        return target_host, action_type
    
    def _update_host_status(self, cyborg, red_action_str, blue_action_str, host_map, ip_map):
        target_host, discovered_subnet, discovered_system, exploited_host, escalated_host = None, None, None, None, None
        reset_host, remove_host, restore_host = None, None, None
        
        # Check Red's actions
        target_host, action_type = self._parse_action(cyborg, red_action_str, 'Red', host_map, ip_map)
        
        if target_host:
            if 'ExploitRemote' in action_type:
                exploited_host = target_host
            elif 'Privilege' in action_type or 'Impact' in action_type:
                escalated_host = target_host
            elif 'DiscoverRemoteSystems' in action_type:
                _cidr = ".".join(target_host.split(".")[:3])
                for ip in ip_map:
                    if _cidr in ip and 'router' in ip_map[ip]:
                        discovered_subnet = ip_map[ip]
                        target_host = discovered_subnet
            elif 'DiscoverNetworkServices' in action_type:
                discovered_system = target_host
                
        # Check Blue's actions
        reset_host, action_type = parse_action(cyborg, blue_action_str, 'Blue', host_map, ip_map)
        if reset_host:
            if 'Remove' in action_type:
                remove_host = reset_host
            elif 'Restore' in action_type:
                restore_host = reset_host
    
        return target_host, reset_host, discovered_subnet, discovered_system, exploited_host, escalated_host, remove_host, restore_host
    
    def create_state_snapshot(self):
        # ... Logic to create and return a snapshot of the current game state ...
        ############
        ## fo viz ##
        ############
        link_diagram = self.cyborg.environment_controller.state.link_diagram
        red_action_str = self.cyborg.get_last_action('Red').__str__()
        blue_action_str = self.cyborg.get_last_action('Blue').__str__()
        
        (
            target_host,
            reset_host,
            discovered_subnet, 
            discovered_system,
            exploited_host,
            escalated_host,
            remove_host,
            restore_host
        ) = self._update_host_status(
            self.cyborg,
            red_action_str,
            blue_action_str,
            self.host_map,
            self.ip_map
        )       

        if discovered_subnet:
            self.discovered_subnets.add(discovered_subnet)

        if discovered_system:
            self.discovered_systems.add(discovered_system)
        
        if exploited_host:
            self.exploited_hosts.add(exploited_host)
            self.compromised_hosts.add(exploited_host)
        if remove_host or restore_host:
            self.exploited_hosts.discard(remove_host)
            self.compromised_hosts.discard(remove_host)
        if escalated_host:
            self.escalated_hosts.add(escalated_host)
            self.compromised_hosts.add(escalated_host)
        if restore_host:
            self.escalated_hosts.discard(restore_host)
            self.compromised_hosts.discard(restore_host)

        # print(self.compromised_hosts)
        
        agent_actions = {
            "Red": {"action": red_action_str, "success": self.cyborg.get_observation('Red')['success'].__str__()},
            "Blue": {"action": blue_action_str, "success": self.cyborg.get_observation('Blue')['success'].__str__()}
        }

        node_colors = [self._get_node_color(node, 
                                      discovered_subnets=self.discovered_subnets,
                                      discovered_systems=self.discovered_systems,
                                      exploited_hosts=self.exploited_hosts, 
                                      escalated_hosts=self.escalated_hosts) 
                       for node in link_diagram.nodes]
        
        node_borders = [self._get_node_border(node, 
                                        target_host=target_host, 
                                        reset_host=reset_host) 
                        for node in link_diagram.nodes]

        state_snapshot = {
            # Populate with necessary state information
            'link_diagram': link_diagram.copy(),  # Assuming link_diagram is a NetworkX graph
            'node_colors': node_colors.copy(),
            'node_borders': node_borders.copy(),
            'compromised_hosts': self.compromised_hosts.copy(),
            # 'exploited_hosts': exploited_hosts.copy(),
            # 'escalated_hosts': escalated_hosts.copy(),
            'agent_actions': agent_actions.copy(),
            # 'ip_map': self.ip_map.copy(),
            'host_map': self.host_map.copy(),
        }

        return state_snapshot

    def reset(self):
        self.compromised_hosts = set()
        self.exploited_hosts = set()
        self.escalated_hosts = set()
        self.discovered_subnets = set()
        self.discovered_systems = set()
        self._create_ip_host_maps()

    def store_state(self, state_snapshot, episode, step):
        self.game_states[self.num_steps][self.red_agent.__class__.__name__][episode][step] = state_snapshot.copy()

    def get_game_state(self):
        return self.game_states
