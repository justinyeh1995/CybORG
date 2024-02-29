import yaml
from typing import Dict, List

class YamlTopologyManager:
    def __init__(self, topology_data: Dict = None):
        self.topology_data = topology_data or {'topo': {'routers': [], 'lans': [], 'links': []}}

    def load_topology(self, file_path: str) -> None:
        with open(file_path, 'r') as file:
            self.topology_data = yaml.safe_load(file)

    def save_topology(self, file_path: str) -> None:
        with open(file_path, 'w') as file:
            yaml.dump(self.topology_data, file, default_flow_style=False, sort_keys=False)

    def get_topology(self) -> Dict:
        return self.topology_data
