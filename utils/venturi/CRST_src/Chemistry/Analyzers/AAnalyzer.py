from Chemistry.Entities.ACRS import ACRS

from abc import ABC, abstractmethod
import networkx as nx


class AAnalyzer(ABC):
    """Class describing an abstract CRS analyzer"""


    MAX_N_RESOLVED_R_NODES = 20


    def __init__(self, associated_CRS:ACRS, show_r_formulas:bool=False) -> None:
        self._CRS = associated_CRS
        """The associated CRS"""
        self.show_r_formulas = show_r_formulas
        """Flag indicating if reactions formulas should be shown as reaction nodes names"""
        self.food_nodes = []
        """List of food nodes names, which are the food names"""
        self.other_species_nodes = []
        """List of other species nodes names, which are the names of the chemical species that are not food"""
        self.reaction_nodes = []
        """List of the reaction nodes names"""
        self.reaction_keys_dict = {}
        """Dictionary associating reactions nodes names to the reaction keys in the CRS"""
        self._init_additional_data_structures()
        self._init_species_nodes()
        self._init_reaction_nodes()
        self.G = self.build_graph()
    

    @abstractmethod
    def _init_additional_data_structures(self) -> None:
        """Initialize additional data structures before setting graph nodes"""
        pass


    @abstractmethod
    def _init_species_nodes(self) -> None:
        """Initialize chemical species graph nodes names"""
        pass


    def _init_reaction_nodes(self) -> None:
        """Initialize reaction graph nodes names as either the reaction formulas or integer numbers"""

        reactions = [r for r in self._CRS.get_all_reactions()]
        if self.show_r_formulas or len(reactions) <= self.MAX_N_RESOLVED_R_NODES:
            for r in reactions:
                self.reaction_keys_dict[r.key] = r.key
        else:
            for i, r in enumerate(reactions):
                self.reaction_keys_dict[i+1] = r.key
        self.reaction_nodes = list(self.reaction_keys_dict.keys())
        

    def build_graph(self) -> nx.Graph:
        """
        Builds a graph representing the system
        """

        G = nx.MultiDiGraph()
        G.add_nodes_from(self.food_nodes, color="red")
        G.add_nodes_from(self.other_species_nodes, color="gray")
        for new_node in self.reaction_nodes:
            G.add_node(new_node, color="white")
            reaction = self._CRS.get_reaction(self.reaction_keys_dict[new_node])
            for reagent in reaction.reagents:
                if reagent in G.nodes:
                    G.add_edge(reagent, new_node)
            for product in reaction.products:
                if product in G.nodes:
                    G.add_edge(new_node, product)
            for catalyst in reaction.catalysts:
                if catalyst in G.nodes:
                    G.add_edge(catalyst, new_node, color="gray")
        return G
