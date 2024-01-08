import matplotlib.pyplot as plt
import networkx as nx
from networkx import connected_components
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class NetworkVisualizer:
    def __init__(self, agent_game_states):
        self.agent_game_states = agent_game_states
        self.type_to_symbol = {
            'router': 'triangle-up',  # Triangle
            'server': 'square',       # Square
            'host': 'circle',         # Circle
            'op_host': 'diamond',
            'op_server': 'square'
        }
        self.seed = 3113794652
        self.save = None
        
    def _get_node_type(self, node):
        type = ""
        if 'router' in node:
            type = 'router'
        elif 'Op' in node:
            if 'Host' in node:
                type = 'op_host'
            else:
                type = 'op_server'
        elif 'Server' in node:
            type = 'server' 
        else:
            type = 'host'
        return type

    def plot(self, save=True):
        self.save = save
        for num_steps in self.agent_game_states:
            for red_agent_name in self.agent_game_states[num_steps]:
                for episode in self.agent_game_states[num_steps][red_agent_name]:
                    for step, state in self.agent_game_states[num_steps][red_agent_name][episode].items():
                        for agent in state:
                            self._plot_state(num_steps, red_agent_name, episode, step, agent, state[agent])

    def _plot_state(self, num_steps, red_agent_name, episode, step, agent, state):
        
        link_diagram = state['link_diagram']
        compromised_hosts = state['compromised_hosts']
        node_colors = state['node_colors']
        node_borders = state['node_borders']
        action_info = state['action_info']
        host_map = state['host_map']

        # 'link_diagram' is the NetworkX graph
        pos = nx.spring_layout(link_diagram, seed=self.seed)
        
        edge_x = []
        edge_y = []
        for edge in link_diagram.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
            
        # Prepare hover text and symbols for each node
        hover_text = []
        node_symbols = []
        node_x = []    
        node_y = []     
        node_names = []

        for i, node in enumerate(link_diagram.nodes()):
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            # Determine the status ...
            compromised = 'Yes' if node in compromised_hosts else 'No'
            node_names.append(node)
            hover_text.append(f"Node: {node}<br>IP Address: {host_map[node]}<br>Compromised: {compromised}")
            # Determine the type of the node and assign the corresponding symbol
            node_type = self._get_node_type(node)  # Replace this with your method to get node type
            node_symbols.append(self.type_to_symbol.get(node_type, 'circle'))  # Default to 'circle'
        
        # Create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=hover_text,
            text=node_names,
            marker=dict(showscale=False, 
                        colorscale='Viridis', 
                        color=node_colors, 
                        line=dict(
                            color=[border['color'] for border in node_borders],  # List of colors for each marker
                            width=[border['width'] for border in node_borders],  # List of widths for each marker
                        ),
                        size=10, 
                        symbol=node_symbols
                       ),
            textposition="top center",  # Position the text above the markers
            textfont=dict(
                family="sans serif",
                size=12,
                color="black")
        )        

        # Create layout
        layout=go.Layout(
                            title=f'<br>Total Number of Steps: {num_steps}\
                                    <br>Red Agent Name: {red_agent_name}\
                                    <br>Episode: {episode+1}\
                                    <br>Display <b>{agent}</b> Agent\
                                    <br>Step {step+1}',
                            title_x=0.0,  # Centers the title
                            title_y=0.85,
                            titlefont_size=12,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                        )
        
        # Create annotations for agent actions, initially invisible
        observations_annotations = []
        vertical_padding = 0.18
        # for idx, action_info in enumerate(action_info):
        observations_annotations.append(dict(
            xref='paper', yref='paper',
            x=0.01, y= 0.2 - vertical_padding,  # Adjust these positions as needed
            text=f"{agent}: <br>{action_info['action']} <br>Success: {action_info['success']}",
            showarrow=False,
            visible=True,  # Initially not visible
            align="left"  # Ensure text is aligned for both agents
        ))
        
        # Prepare and plot the figure
        fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
        self._setup_annotations_and_buttons(fig, observations_annotations)

        # Save and show the figure
        if self.save:
            self._save_figure(fig, red_agent, step)
            
        fig.show()

    def _setup_annotations_and_buttons(self, fig, annotations):
        # ... code to set up annotations and buttons ...
        # Add a button to toggle the visibility of observation annotations
        fig.update_layout(
            width=1000,
            annotations=annotations,  # Include the annotations by default
            updatemenus=[
                dict(
                    buttons=list([
                        dict(label="Show Observations",
                             method="update",
                             args=[{"visible": [True, True, True, True]},  # Set the visibility as required
                                   {"annotations": annotations}]),
                        dict(label="Hide Observations",
                             method="update",
                             args=[{"visible": [True, True, True, False]},  # Reset to original visibility
                                   {"annotations": []}])
                    ]),
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    # x=0.05,
                    # xanchor="left",
                    y=0.5,
                    # yanchor="top"
                )
            ]
        )
        
    def _save_figure(self, fig, red_agent, step):
        image_folder = f"images/{red_agent}"
        if not os.path.exists(image_folder):
            os.makedirs(image_folder, exist_ok=True)
        fig.write_image(f"{image_folder}/step{step+1}.png")
        