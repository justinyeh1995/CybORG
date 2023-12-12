#@author : harsh Vardhan (Vanderbilt university)

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.State import State
from pprint import pprint
import matplotlib.pyplot as plt
import networkx as nx
from networkx import connected_components

class Isolate(Action):
    def __init__(self, session: int, agent: str, hostname: str):
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname

    def execute(self, state: State) -> Observation:
        # WIP: working to implement the 'Isolate' functionality to the cyborg
        print('%%%%%%%%%%%%%%')
        parent_session: VelociraptorServer = state.sessions[self.agent][self.session]
        # find relevant session on the chosen host
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        print('Session is:',sessions)
        print('State variables are:')
        pprint(state.__dict__)
        print('--> link diagram:')
        pprint(state.link_diagram.__dict__)
        nx.draw(state.link_diagram,with_labels=True, font_weight='bold')
        plt.show()
        if len(sessions) > 0:
            session = state.np_random.choice(sessions)
           
            print('--> link diagram:')
            try: 
              state.link_diagram.remove_node(self.hostname)
              state.connected_components = [i for i in connected_components(state.link_diagram)]
              state.hosts = {key:val for key, val in state.hosts.items() if val != self.hostname}
              state.ip_addresses = {key:val for key, val in state.ip_addresses.items() if val != self.hostname}
            
              pprint(state.__dict__)
              pprint(state.link_diagram.__dict__)
            except:  
              pass
            finally: 
              nx.draw(state.link_diagram,with_labels=True, font_weight='bold')
              plt.show()
              obs = Observation(True)
              # To do: remove the host from the subnet
              if self.hostname in parent_session.sus_pids:
                pass
              return obs
        else:
            return Observation(False)


    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
    
