import subprocess
import inspect
import time
import os
from statistics import mean, stdev
import random
import collections
import traceback 
from pprint import pprint

# import matplotlib.pyplot as plt
# import networkx as nx
# from networkx import connected_components
# import plotly.graph_objects as go
# import plotly.express as px
import pandas as pd
from dataclasses import dataclass

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Agents import B_lineAgent, BlueReactRestoreAgent, BlueReactRemoveAgent, \
    RandomAgent, RedMeanderAgent, SleepAgent
from CybORG.Agents import BaseAgent
from CybORG.Agents.MainAgent import MainAgent
from CybORG.Agents.MainAgent_cyborg_mm import MainAgent as MainAgent_cyborg_mm

from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Agents.Wrappers.ChallengeWrapper2 import ChallengeWrapper2
from CybORG.Agents.Wrappers import EnumActionWrapper
from CybORG.Agents.Wrappers.FixedFlatWrapper import FixedFlatWrapper
from CybORG.Agents.Wrappers.IntListToAction import IntListToActionWrapper
from CybORG.Agents.Wrappers.OpenAIGymWrapper import OpenAIGymWrapper
from CybORG.Simulator.Scenarios.FileReaderScenarioGenerator import FileReaderScenarioGenerator

from CybORG.Tutorial.Visualizers import NetworkVisualizer
from CybORG.Tutorial.GameStateManager import GameStateManager
from CybORG.Tutorial.Mininet.MininetAdapter import MininetAdapter

MAX_EPS = 1
agent_name = 'Blue'
random.seed(0)
cyborg_version = CYBORG_VERSION
# scenario = 'Scenario2'
scenario = 'Scenario2_cyborg--'

@dataclass
class AgentFactory:
    """Class for keeping building agents."""
    
    def create(self, type: str) -> BaseAgent:
        if type == "CardiffUni":
            return MainAgent()
        elif type == "CASTLEgym":
            return MainAgent_cyborg_mm()
        else:
            return BlueReactRemoveAgent()  

@dataclass
class CybORGFactory:
    """Class for keeping building agents."""
    type: str = "wrap"
    file_name: str = "Scenario2_cyborg--"
    
    def wrap(self, env):
        # return ChallengeWrapper2(env=env, agent_name='Blue')
        return ChallengeWrapper(env=env, agent_name='Blue')
    
    def create(self, type: str, red_agent) -> BaseAgent:
        red_agent = red_agent()
        path = str(inspect.getfile(CybORG))
        path = path[:-7] + f'/Simulator/Scenarios/scenario_files/{self.file_name}.yaml'
        sg = FileReaderScenarioGenerator(path)
        cyborg = CybORG(sg, 'sim', agents={'Red': red_agent})
        
        if type == "wrap":
            return self.wrap(cyborg)
            
        return cyborg

def wrap(env):
    # return ChallengeWrapper2(env=env, agent_name='Blue')
    return ChallengeWrapper(env=env, agent_name='Blue')


def main(agent_type: str, cyborg_type: str) -> None:
    cyborg_version = CYBORG_VERSION
    scenario = 'Scenario2_cyborg--'
    # commit_hash = get_git_revision_hash()
    commit_hash = "Not using git"
    # ask for a name
    name = "John Hannay"
    # ask for a team
    team = "CardiffUni"
    # ask for a name for the agent
    name_of_agent = "PPO + Greedy decoys"

    lines = inspect.getsource(wrap)
    wrap_line = lines.split('\n')[1].split('return ')[1]

    # Change this line to load your agent
    agent_factory = AgentFactory()
    # Change this line to load your agent
    agent = agent_factory.create(type=agent_type)
    
    print(f'Using agent {agent.__class__.__name__}, if this is incorrect please update the code to load in your agent')

    cyborg_factory = CybORGFactory()

    print(f'using CybORG v{cyborg_version}, {scenario}\n')
    
    # game manager initialization
    game_state_manager = GameStateManager()
    # mininet adapter initialization
    mininet_adapter = MininetAdapter()

    
    for num_steps in [10]:
        for red_agent in [B_lineAgent]:
            
            cyborg = cyborg_factory.create(type=cyborg_type, red_agent=red_agent)

            observation = cyborg.reset()
            # print('observation is:',observation)
            
            # Rest set up game_state_manager
            game_state_manager.set_environment(cyborg=cyborg,
                                               red_agent=red_agent,
                                               blue_agent=agent,
                                               num_steps=num_steps)
            game_state_manager.reset()


            # Reset mininet adapter 
            mininet_adapter.set_environment(cyborg=cyborg)
            mininet_adapter.reset()
            
            
            action_space = cyborg.get_action_space(agent_name)

            total_reward = []
            actions = []
            for i in range(MAX_EPS):
                r = []
                a = []
                
                # cyborg.env.env.tracker.render()
                for j in range(num_steps):
                    blue_action_space = cyborg.get_action_space('Blue')
                    blue_obs = cyborg.get_observation('Blue') # get the newest observation
                    blue_action = agent.get_action(blue_obs, blue_action_space)
                    # pprint(blue_action)
                        
                    result = cyborg.step('Blue', blue_action, skip_valid_action_check=False)
                    
                    # create state for this step
                    state_snapshot = game_state_manager.create_state_snapshot()
                    # The adapter should pass the action as a param
                    mininet_adapter.perform_emulation()
                    # pprint(mininet_adapter)
                    # game_state_manager.update_state_snapshot(mininet_adapter)
                    # game manager store state
                    game_state_manager.store_state(state_snapshot, i, j)
                    
                # game manager reset
                agent.end_episode()
                total_reward.append(sum(r))
                actions.append(a)
                # observation = cyborg.reset().observation
                observation = cyborg.reset()
                # game state manager reset
                game_state_manager.reset()
                # mininet adapter reset
                mininet_adapter.reset()
        
        mininet_adapter.clean()

    return game_state_manager.get_game_state()


if __name__ == "__main__":
    game_simple_agent_state = main(agent_type="default", cyborg_type="simple")
    # game_castle_gym_agent_state = main(agent_type="CASTLEgym", cyborg_type="wrap")


    