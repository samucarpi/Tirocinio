from .ACRS import ACRS
from Chemistry.Entities.Reaction import Reaction

from abc import ABC, abstractmethod
from copy import copy
from logging import getLogger


class AAutocatSet(ABC):
    """
    Abstract class defining an autocatalytic and food-generated set of reactions relatively to its associated CRS
    """


    LOGGER = getLogger(__name__)


    def __init__(self, associated_CRS:ACRS) -> None:
        """
        Initializer

        The associated CRS is copied, so its representation in the class if frozen in time
        :param associated_CRS: the associated CRS
        :return None:
        :raise ValueError: if the associated CRS does not contain an autocatalytic set
        """

        self._CRS = copy(associated_CRS)
        self.reaction_set = self.get_max_set()
        """
        The reaction set is actually a list to preserve reaction order of the associated CRS
        """
        if len(self.reaction_set) == 0:
            raise ValueError(f"The CRS does not contain a {self.get_type()}")
    

    @abstractmethod
    def get_type(self) -> str:
        """Get the autocatalytic set type"""
        pass


    @abstractmethod
    def get_max_set(self) -> list[str]:
        """
        Calculate the maximal autocatalytic set of reactions present in the associated CRS

        :return: the reactions of the set, in the form of a list of reaction keys
        """
        pass


    def _get_closure(self, ch_species:set[str], reactions:list[Reaction]) -> set[str]:
        """
        Calculate the closure of a set of chemical species relative to a list of reactions and returns it
        
        The closure of the initial set of chemical species is obtained by adding all the species that can be obtained
        by repeated applications of the reactions of the dictionary, whether they are catalyzed or not;
        the function is used by utilities that determine auto-catalytic sets of reactions in a CRS
        :param ch_species: set of chemical species names
        :param reactions: list of reactions
        :return: the closure of the initial set of chemical species
        """

        W = ch_species.copy()
        change = True
        while (change):
            change = False
            for reaction in reactions:
                A = set(reaction.reagents)
                B = set(reaction.products)
                if A.issubset(W) and not B.issubset(W):
                    W = W | B
                    change = True
                    break
        return W
    

    def get_shrinked_CRS(self) -> ACRS:
        """
        Get a version of the associated CRS shrinked to the autocatalytic reaction set;
        the shrinking is done by removing all the reactions that are not in the set and all the not-involved chemical species.

        The original associated CRS is not modified, nor is the internal representation
        :return: the shrinked version of the associated CRS
        """

        shrinked_CRS = copy(self._CRS)
        # get a list of all chemical species names appearing in the reaction set
        all_set_species_names = set()
        for k in self.reaction_set:
            reaction = shrinked_CRS.get_reaction(k)
            all_set_species_names = all_set_species_names.union(set(reaction.get_all_species_names()))

        for reaction in shrinked_CRS.get_all_reactions():
            if not reaction.key in self.reaction_set:
                # the return value is not checked since the reactions keys are taken directly from the CRS
                # whose representation is frozen in time
                shrinked_CRS.delete_reaction(reaction.key)

        # a chemical species of the original CRS is part of the shrinked one if its name appears in the list of allSubsetSpeciesNames
        for ch_species_name in shrinked_CRS.get_reactive_species_names():
            if not ch_species_name in all_set_species_names:
                # the return value is not checked since the species keys are taken directly from the CRS and they are not containers
                shrinked_CRS.delete_ch_species(ch_species_name)

        self.LOGGER.info(f"CRS reduced to autocatalytic set\n{shrinked_CRS.to_string()}")
        return shrinked_CRS
        