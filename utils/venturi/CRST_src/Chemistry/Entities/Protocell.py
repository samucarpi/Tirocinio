import Environment as Env

from .ACRS import ACRS
from .ChemicalSpecies import ChemicalSpecies
from .ExtInteraction import ExtInteraction



class Protocell(ACRS):
    """
    Class defining a protocell, a specific type of Chemical Reaction System (CRS)
    """


    @classmethod
    def get_type_string(cls) -> str:
        return Env.CRS_PTC
    
    
    def add_ch_species(self, ch_species:ChemicalSpecies) -> bool:
        """
        Tries to add a chemical species to the system

        :param ch_species: the chemical species to be added
        :return: True if the addition is successful, False otherwise
        """

        if ch_species.name in self._ch_species:
            return False

        self._ch_species[ch_species.name] = ch_species
        self.LOGGER.info(f"Chemical species {ch_species.name} added to the system")

        return True
        

    def set_as_food(self, food:str, ext_int:ExtInteraction=None) -> bool:
        """
        Tries to set an existing chemical species as food for the protocell, also setting the correspondant osmosis

        :param food: the chemical species name to be set as food
        :param ext_int: the external interactions to be set, must be an osmosis coherent with the food chosen;
            if it is not specified, a default osmosis is added
        :return: True if the operation is successful, False otherwise
        """
        
        if ext_int == None:
            ext_int = ExtInteraction(food, Env.EI_OSM, Env.DEF_OSM_K, Env.DEF_OSM_ECONC)

        return self._set_food_with_defined_int(food,ext_int,Env.EI_OSM)

