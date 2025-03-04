import Environment as Env

from .AAutocatSet import AAutocatSet

import logging


class CAF(AAutocatSet):
    """
    Class defining a Constructively Autocatalytic and Food-generated set of reactions (CAF)
    relatively to its associated CRS
    """


    LOGGER = logging.getLogger(__name__)


    @classmethod
    def get_type(cls) -> str:
        return Env.ACS_CAF


    @classmethod
    def get_description(cls) -> str:
        return "Constructively Autocatalytic and Food-generated set of reactions (CAF)"


    def get_max_set(self) -> list[str]:
        """
        Calculate the maximal Constructively Autocatalytic and Food-generated set of reactions (CAF)
        present in the associated CRS with Hordijk algorithm
        
        CAF is a more restrict notion compared to RAF: the reactions of the subset can be enumerated in such a way that
        for each reaction in this ordering, each reagent and at least one catalyst is produced by some earlier reaction
        :return: the reactions of the subset, in the form of a list of reaction keys
        """
        
        W = set(self._CRS.get_foods_names())
        S = {}
        change = True
        while (change):
            change = False
            for reaction in self._CRS.get_all_reactions():
                A = set(reaction.reagents)
                B = set(reaction.products)
                # it the reagents are in the expanded (or not) food set and the reaction is not already in the set under construction
                if A.issubset(W) and reaction.key not in S.keys():
                    # also check if at least one of the catalysts of the reaction is in the food set
                    for catalyst in reaction.catalysts:
                        if catalyst in W:
                            # in this case expand the food set with the reactions products and add the reaction to the set
                            W = W | B
                            S[reaction.key] = reaction
                            self.LOGGER.debug(
                                f"Reaction {reaction.key} catalyst added to the CAF: at least one catalyst in the food set")
                            change = True
                            break
        keys = [k for k in S.keys()]
        self.LOGGER.debug(f"List of reactions keys of the CAF: {list(keys)}")
        return keys

    