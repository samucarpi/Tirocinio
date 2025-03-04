import Environment as Env

from .AAutocatSet import AAutocatSet
import logging


class RAF(AAutocatSet):
    """
    Class defining a Reflexively Autocatalytic and Food-generated set of reactions (RAF)
    relatively to its associated CRS
    """


    LOGGER = logging.getLogger(__name__)


    @classmethod
    def get_type(cls) -> str:
        return Env.ACS_RAF
    

    @classmethod
    def get_description(cls) -> str:
        return "Reflexively Autocatalytic and Food-generated set of reactions (RAF)"


    def get_max_set(self) -> list[str]:
        """
        Calculate the maximal Reflexively Autocatalytic and Food-generated set of reactions (RAF) present in the associated CRS
        with Hordijk algorithm
        
        A subset of reactions is a RAF if, for each of its reactions, at least one of the catalysts and all reactants
        are in the closure of the food set relative to the set of reactions itself
        :return: the reactions of the set, in the form of a list of reaction keys
        """
        
        R = self._CRS.get_all_reactions()
        change = True
        while (change):
            change = False
            closure = self._get_closure(set(self._CRS.get_foods_names()), R)
            for reaction in R:
                A = set(reaction.reagents)
                # if, for the reaction, not all the reagents are in the closure or none of the catalysts are
                if not A.issubset(closure) or len(set(reaction.catalysts).intersection(closure)) == 0:
                    # remove the reaction from the dictionary
                    R.remove(reaction)
                    self.LOGGER.debug(
                        f"Reaction {reaction.key} deleted from the RAF: not all the reagents or none of the catalysts in the closure")
                    change = True
                    break
        keys = [reaction.key for reaction in R]
        self.LOGGER.debug(f"List of reaction keys of the RAF: {list(keys)}")
        return keys




    