import Environment as Env

from Chemistry.Entities.ACRS import ACRS

from abc import ABC, abstractmethod
from logging import getLogger


class AAddReactionStrategy(ABC):
    """
    Abstract class defining a strategy to add reactions to an existing Chemical Reaction System (CRS)
    """
    

    LOGGER = getLogger(__name__)


    def __init__(
            self,
            alphabet:str,
            reactions_weights:dict[str, float],
            cat_range:tuple[int, int],
            no_food_cat: bool,
        ) -> None:
        """
        Initializer

        :param alphabet: the alphabet
        :param reactions_weights: the reaction types supported associated to the relative weight on total reactions,
            expressed as a float between 0 and 1
        :param cat_range: the range for the number of catalyzers to be present in reactions created
        :param no_food_cat: flag indicating if food of the CRS should be considered as valid catalyzer species
        :return: None
        """

        self._CRS:ACRS = None
        self._alphabet = alphabet
        self._reactive_species_names = list()
        self._catalyzers_names = list()
        self.n_react_upper_bound = int(0)

        # define supported reaction types
        self.supported_react_types:list[str] = []
        for r_type in reactions_weights:
            if not r_type in Env.R_TYPES:
                self.LOGGER.warning(f"Reaction type {r_type} not recognized")
            self.supported_react_types.append(r_type)
        if len(self.supported_react_types) == 0:
            self.LOGGER.warning(f"No valid reaction types specified, defaulting to {Env.R_CLEAVE}s and {Env.R_COND}s")
            self.supported_react_types = [Env.R_CLEAVE,Env.R_COND]

        self._weights:list[float] = []
        """numerical weights (floats between 0 and 1) of supported reactions"""
        for r_type in self.supported_react_types:
            relative_abundance = reactions_weights.get(r_type, 0)
            self._weights.append(relative_abundance)

        # define catalyzers parameters
        self._no_food_cat = no_food_cat
        self._cat_range = cat_range

        self._calibrated = False


    @abstractmethod
    def apply(self) -> int:
        """
        Apply the strategy to add reactions

        The strategy needs to be calibrated on a specific CRS before attempting to apply it
        After the strategy has been fully applied, it should be reset
        :return: the number of reactions added
            in case the call returns 0, it can be assumed the CRS can't hold any more reactions
        """
        pass

        
    def _can_be_applied(self) -> bool:
        """
        Check the strategy applicability
        
        :return: True if the strategy can be applied, False otherwise
        """

        if not self._calibrated:
            self.LOGGER.info("Strategy not calibrated")
            return False
        
        if len(self._reactive_species_names) == 0:
            self.LOGGER.info("The CRS doesn't contain reactive chemical species")
            return False
    
        return True


    def calibrate(self, CRS:ACRS) -> None:
        """
        Calibrate the strategy on a specific CRS

        :param CRS: the CRS which undergoes direct transformation
        """

        self._CRS = CRS
        self._reactive_species_names = CRS.get_reactive_species_names()
        self._catalyzers_names = CRS.get_reactive_species_names(no_food=self._no_food_cat)
        self.n_react_upper_bound = self._max_n_reactions()
        self._calibrated = True
    

    def reset(self) -> None:
        """
        Reset the strategy, unsetting the "calibrated" flag
        """    

        self._calibrated = False


    def _max_n_reactions(self) -> int:
        """
        Calcultes an upper bound for the number of reactions in the CRS
        
        The calculation makes use of Kauffman formula to set an upper bound for number of possible cleavages
        and condensations, extended to consider exchanges as well; it is assumed that for every species all reactions are possible,
        without checking if the products are actually amongst the species;
        as a result, this is just an exaggerated guess, but it is useful as an upper bound
        :return: the upper bound
        """

        max_species_name_length = max(len(name) for name in self._reactive_species_names)
        max_n_reactions, tot_cleavages, tot_condensations, tot_exchanges = 0, 0, 0, 0
        # for every possible chemical species determine the total number of possible reactions that can create that species,
        # and add it to the "max_n_reactions" accumulator
        for ch_species_name in self._reactive_species_names:
            l = len(ch_species_name)
            n_cleavages = 0
            for i in range(l+1, max_species_name_length+1):
                n_cleavages += 2*len(self._alphabet)**(i-l)
            tot_cleavages += n_cleavages

            n_condensations = l-1
            tot_condensations += n_condensations

            ### TO DO: double check calculation
            n_exchanges = 0
            for i in range(1, l):
                for j in range(i+1, max_species_name_length+1):
                    n_exchanges += 2*len(self._alphabet)**(j-l)
            tot_exchanges += n_exchanges
        
        # consider only the reactions types that are supported by the strategy
        n_react_dict = {Env.R_CLEAVE:tot_cleavages, Env.R_COND:tot_condensations, Env.R_EXCH:tot_exchanges}
        for k, val in n_react_dict.items():
            if k in self.supported_react_types:
                max_n_reactions += val
        # since any reaction created by the class can be catalyzed by a  defined maximum number of catalyzers species,
        # and every single catalyzer is part of the reaction key,
        # the maximum number of reactions has to be multiplied by a factor that is
        # the number of reactive species power the maximum number of catalyzers per reaction
        n_catalyzers = len(self._catalyzers_names)
        max_n_cat_react = self._cat_range[1]
        return max_n_reactions * (pow(n_catalyzers, max_n_cat_react))
    