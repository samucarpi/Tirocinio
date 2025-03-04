import Environment as Env

from .ACRS import ACRS
from .ChemicalSpecies import ChemicalSpecies
from .ExtInteraction import ExtInteraction


class Chemostat(ACRS):
    """
    Class defining a chemostat, a specific type of Chemical Reaction System (CRS)
    """


    @classmethod
    def get_type_string(cls) -> str:
        return Env.CRS_CSTR
    

    def add_ch_species(self, ch_species:ChemicalSpecies, ext_int:ExtInteraction=None) -> bool:
        """
        Tries to add a chemical species to the system, also defining a depletion external interaction

        :param ch_species: the chemical species to be added
        :param ext_int: the external interactions to be set, must be a depletion coherent with the chemical species added;
            if it is not specified, a default depletion is added
        :return: True if the addition is successful, False otherwise
        """

        if ch_species.name in self._ch_species:
            return False

        if ext_int == None:
            ext_int = ExtInteraction(ch_species.name, Env.EI_OUT, Env.DEF_OUT_K)
        elif not ext_int.int_type == Env.EI_OUT or not ext_int.ch_species_name == ch_species.name:
            return False
        if ext_int.key in self._ext_interactions:
            return False
        
        self._ch_species[ch_species.name] = ch_species
        self.LOGGER.info(f"Chemical species {ch_species.name} added to the system")
        self._ext_interactions[ext_int.key] = ext_int
        self.LOGGER.info(f"External interaction {ext_int.key} added to the system")

        return True
        

    def set_as_food(self, food:str, ext_int:ExtInteraction=None) -> bool:
        """
        Tries to set an existing chemical species as food for the chemostat, also setting the correspondant injection

        :param food: the chemical species name to be set as food
        :param ext_int: the external interactions to be set, must be an injection coherent with the food chosen;
            if it is not specified, a default injection is added
        :return: True if the operation is successful, False otherwise
        """

        if ext_int == None:
            ext_int = ExtInteraction(food, Env.EI_IN, Env.DEF_IN_K)

        return self._set_food_with_defined_int(food,ext_int,Env.EI_IN)