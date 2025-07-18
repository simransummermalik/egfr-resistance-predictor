import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np

class PathwayVisualizer:
    """Creates pathway and network visualizations for EGFR mutations"""
    
    def __init__(self):
        self.pathway_nodes = self._define_pathway_nodes()
        self.pathway_edges = self._define_pathway_edges()
    
    def _define_pathway_nodes(self):
        """Define key nodes in EGFR signaling pathways"""
        return {
            'EGFR': {'x': 0, 'y': 0, 'color': '#1f77b4', 'size': 30},
            'RAS': {'x': -2, 'y': -2, 'color': '#ff7f0e', 'size': 25},
            'RAF': {'x': -2, 'y': -3, 'color': '#ff7f0e', 'size': 20},
            'MEK': {'x': -2, 'y': -4, 'color': '#ff7f0e', 'size': 20},
            'ERK': {'x': -2, 'y': -5, 'color': '#ff7f0e', 'size': 20},
            'PI3K': {'x': 2, 'y': -2, 'color': '#2ca02c', 'size': 25},
            'AKT': {'x': 2, 'y': -3, 'color': '#2ca02c', 'size': 20},
            'mTOR': {'x': 2, 'y': -4, 'color': '#2ca02c', 'size': 20},
            'JAK': {'x': 0, 'y': -2, 'color': '#d62728', 'size': 20},
            'STAT': {'x': 0, 'y': -3, 'color': '#d62728', 'size': 20},
            'Proliferation': {'x': -1, 'y': -6, 'color': '#9467bd', 'size': 25},
            'Survival': {'x': 1, 'y': -6, 'color': '#8c564b', 'size': 25}
        }
    
    def _define_pathway_edges(self):
        """Define connections between pathway nodes"""
        return [
            ('EGFR', 'RAS'), ('RAS', 'RAF'), ('RAF', 'MEK'), ('MEK', 'ERK'),
            ('EGFR', 'PI3K'), ('PI3K', 'AKT'), ('AKT', 'mTOR'),
            ('EGFR', 'JAK'), ('JAK', 'STAT'),
            ('ERK', 'Proliferation'), ('STAT', 'Proliferation'),
            ('AKT', 'Survival'), ('mTOR', 'Survival')
        ]
    
    def create_pathway_diagram(self, results):
        """Create interactive pathway diagram showing mutation effects"""
        fig = go.Figure()
        
        # Determine which pathways are affected
        affected_pathways = set()
        for result in results:
            affected_pathways.update(result['analysis']['affected_pathways'])
        
        # Add nodes
        for node_name, node_info in self.pathway_nodes.items():
            # Determine if node should be highlighted
            is_affected = any(pathway in node_name or node_name in pathway 
                            for pathway in affected_pathways)
            
            color = '#ff4444' if is_affected else node_info['color']
            size = node_info['size'] + 10 if is_affected else node_info['size']
            
            fig.add_trace(go.Scatter(
                x=[node_info['x']],
                y=[node_info['y']],
                mode='markers+text',
                marker=dict(size=size, color=color),
                text=node_name,
                textposition="middle center",
                name=node_name,
                showlegend=False
            ))
        
        # Add edges
        for edge in self.pathway_edges:
            start_node = self.pathway_nodes[edge[0]]
            end_node = self.pathway_nodes[edge[1]]
            
            fig.add_trace(go.Scatter(
                x=[start_node['x'], end_node['x']],
                y=[start_node['y'], end_node['y']],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False
            ))
        
        fig.update_layout(
            title="EGFR Signaling Pathway Impact",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=500
        )
        
        return fig
    
    def create_mutation_landscape(self, results):
        """Create mutation landscape visualization"""
        mutations = []
        resistance_scores = []
        mutation_types = []
        
        for result in results:
            mutations.append(f"{result['mutation']['detail']}")
            resistance_scores.append(result['analysis']['resistance_score'])
            mutation_types.append(result['mutation']['type'])
        
        fig = go.Figure(data=go.Scatter(
            x=list(range(len(mutations))),
            y=resistance_scores,
            mode='markers+text',
            marker=dict(
                size=[20 + score * 30 for score in resistance_scores],
                color=resistance_scores,
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Resistance Score")
            ),
            text=mutations,
            textposition="top center"
        ))
        
        fig.update_layout(
            title="Mutation Resistance Landscape",
            xaxis_title="Mutation Index",
            yaxis_title="Resistance Score",
            yaxis=dict(range=[0, 1])
        )
        
        return fig
    
    def create_drug_efficacy_heatmap(self, results):
        """Create drug efficacy heatmap"""
        # Extract drug recommendations
        all_drugs = set()
        mutations = []
        
        for result in results:
            mutations.append(result['mutation']['detail'])
            for rec in result['analysis']['drug_recommendations']:
                all_drugs.add(rec['name'])
        
        # Create efficacy matrix
        efficacy_matrix = []
        drug_list = list(all_drugs)
        
        for result in results:
            row = []
            mutation_drugs = {rec['name']: rec['efficacy'] 
                            for rec in result['analysis']['drug_recommendations']}
            
            for drug in drug_list:
                if drug in mutation_drugs:
                    efficacy = mutation_drugs[drug]
                    if efficacy == "High":
                        row.append(3)
                    elif efficacy == "Medium":
                        row.append(2)
                    elif efficacy == "Low":
                        row.append(1)
                    else:
                        row.append(0)
                else:
                    row.append(0)
            efficacy_matrix.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=efficacy_matrix,
            x=drug_list,
            y=mutations,
            colorscale='RdYlGn',
            colorbar=dict(
                title="Efficacy",
                tickvals=[0, 1, 2, 3],
                ticktext=["None", "Low", "Medium", "High"]
            )
        ))
        
        fig.update_layout(
            title="Drug Efficacy by Mutation",
            xaxis_title="Drugs",
            yaxis_title="Mutations"
        )
        
        return fig
