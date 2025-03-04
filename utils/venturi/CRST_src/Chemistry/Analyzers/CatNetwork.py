from .AAnalyzer import AAnalyzer

from logging import getLogger


class CatNetwork(AAnalyzer):
    """
    Class to analyze the catalyses network of a Chemical Reaction System (CRS)
    """


    LOGGER = getLogger(__name__)


    def _init_additional_data_structures(self) -> None:
        self.catalyses = set(self._CRS.get_all_catalyses())
        catalysts_names = set([cat[0] for cat in self.catalyses])
        self.catalysts_list = list(catalysts_names)


    def _init_species_nodes(self) -> None:
        food_names = self._CRS.get_foods_names()
        for catalyst in self.catalysts_list:
            if catalyst in food_names:
                self.food_nodes.append(catalyst)
            else:
                self.other_species_nodes.append(catalyst)


    def get_autocat_species(self) -> list[str]:
        """
        Get a list of all the catalysts that catalyze at least one of their own production reactions

        :return: list of strings
        """

        autocat_sp = set()
        for catalyst in self.catalysts_list:
            for catalyses in self.catalyses:
                if catalyses[0] == catalyst:
                    reaction = self._CRS.get_reaction(catalyses[1])
                    n_occ_reag = reaction.reagents.count(catalyst)
                    n_occ_prod = reaction.products.count(catalyst)
                    if n_occ_prod-n_occ_reag > 0:
                        self.LOGGER.info(f"Autocatalyzer found: {catalyst}, reaction {reaction.key}")
                        autocat_sp.add(catalyst)
        return list(autocat_sp)
    

    def get_consumed_species(self) -> list[str]:
        """
        Get a list of all the catalysts that are consumed in at least one reaction

        :return: list of strings
        """

        consumed_sp = set()
        for catalyst in self.catalysts_list:
            for reaction in self._CRS.get_all_reactions():
                n_occ_reag = reaction.reagents.count(catalyst)
                n_occ_prod = reaction.products.count(catalyst)
                if n_occ_reag-n_occ_prod > 0:
                    self.LOGGER.info(f"Consumed catalizer found: {catalyst}, reaction {reaction.key}")
                    consumed_sp.add(catalyst)
        return list(consumed_sp)
    

    def get_n_reactions_catalyzed(self, catalyst:str) -> int:
        """
        Get the number of reaction catalyzed by the specifies catalyst
        
        :return: the number of reactions catalyzed
        """

        catalysts_in_catalyses_list = [cat[0] for cat in self.catalyses]
        n_react = catalysts_in_catalyses_list.count(catalyst)
        return n_react


    def get_reactions_catalyzed_distribution(self) -> dict[int,int]:
        """
        Get the distribution of number of reactions catalyzed by the catalystc of the network

        The entire newtwork is checked and every possible value n of different reactions catalyzed by the various catalysts is desumed;
        on this basis the distribution of values n amongst the catalysts is calculated:
        specifically at every values n is associated the number of catalysts that catalyze exactly n reactions
        return: a dictionary representing the distribuion of number of reactions catalyzed by the catalysts
        """
        
        cat_nreact_dict = {}
        max_n = 0
        for catalyst in self.catalysts_list:
            n_react = self.get_n_reactions_catalyzed(catalyst)
            cat_nreact_dict[catalyst] = n_react
            if n_react > max_n:
                max_n = n_react
        nreact_dist = {}
        cat_nreact_list = list(v for v in cat_nreact_dict.values())
        for i in range(1,max_n+1):
            n_react_i = cat_nreact_list.count(i)
            nreact_dist[i] = n_react_i
            self.LOGGER.info(f"Catalyzers catalyzing {i} reactions in the network: {n_react_i}")
        return nreact_dist


