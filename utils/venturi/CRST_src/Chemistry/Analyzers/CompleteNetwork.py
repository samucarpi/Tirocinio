from .AAnalyzer import AAnalyzer


class CompleteNetwork(AAnalyzer):
    """Class describing a complete network of a CRS as a graph"""


    def _init_additional_data_structures(self) -> None:
        pass


    def _init_species_nodes(self) -> None:
        self.food_nodes = self._CRS.get_foods_names()
        self.other_species_nodes = self._CRS.get_reactive_species_names(no_food=True)




