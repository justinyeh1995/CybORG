import traceback 

class ActionTranslator:
    def translate(self, action):
        raise NotImplementedError

class RedActionTranslator(ActionTranslator):
    def translate(self, action_type, target_host, cyborg_to_mininet_host_map) -> str:
        host = cyborg_to_mininet_host_map['User0'] # red host is always user0
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
            action = "ping -c 1" # dummy
            target = "nat0" # dummy
        else:
            action = "sleep 1" # dummy
            target = "" # dummy
            
        cmd = f'{host} timeout {timeout} {action} {target}'
        
        return cmd

class BlueActionTranslator(ActionTranslator):
    def translate(self, action_type, target_host, cyborg_to_mininet_host_map) -> str:
        timeout = 10
        # @To-Do code smells
        # blue host is undecided at the moment
        if action_type == "Remove":
            print("Blue Remove")
        elif action_type == "Restore":
            print("Blue Restore")
        elif action_type == "Monitor":
            print("Blue Monitor")
        host = target_host
        action = ""
        cmd = f'{host} timeout {timeout} {action}'
        cmd = 'lan1h1 ping -c 1 lan2h2'
        return cmd