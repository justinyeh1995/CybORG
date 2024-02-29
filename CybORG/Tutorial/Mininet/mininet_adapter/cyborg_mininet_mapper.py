class CybORGMininetMapper:
    def __init__(self):
        self.cyborg_to_mininet_map = {}
        self.mininet_to_cyborg_map = {}

    def update_mapping(self, cyborg_entities: Dict, mininet_entities: Dict) -> None:
        self.cyborg_to_mininet_map = {cyborg: mininet for cyborg, mininet in zip(cyborg_entities.keys(), mininet_entities.keys())}
        self.mininet_to_cyborg_map = {mininet: cyborg for cyborg, mininet in zip(cyborg_entities.keys(), mininet_entities.keys())}

    def get_mininet_entity(self, cyborg_entity: str) -> str:
        return self.cyborg_to_mininet_map.get(cyborg_entity, "")

    def get_cyborg_entity(self, mininet_entity: str) -> str:
        return self.mininet_to_cyborg_map.get(mininet_entity, "")
