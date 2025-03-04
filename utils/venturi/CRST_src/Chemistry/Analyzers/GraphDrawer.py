import matplotlib.pyplot as plt
import networkx as nx


class GraphDrawer:
    """Class to draw a graph, with associated nodes and edges colors"""


    def __init__(self, graph:nx.Graph) -> None:
        self.G = graph

    
    def draw(self) -> None:
        """Draw the graph"""
        
        nodes_colors_list = [c for (v,c) in self.G.nodes.data("color", default="black")]
        edges_colors_list = [c for (u,v,c) in self.G.edges.data("color", default="black")]
        nx.draw(self.G, with_labels=True, node_color = nodes_colors_list, edge_color = edges_colors_list)
        plt.show()
