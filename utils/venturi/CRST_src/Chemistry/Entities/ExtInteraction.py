import Environment as Env

from math import isclose


class ExtInteraction:
    """
    Class describing an interaction between the enxternal envinronment and the CRS
    """


    def __init__(self, sp_name:str, int_type:str, int_constant:float, ext_conc:float=Env.DEF_OSM_ECONC) -> None:
        """
        Initializer
        :param sp_name: the unique chemical species name interested by the interaction
        :param int_type: type of interaction, must be one of the constants indicated in Env.EI_TYPES
        :param int_constant: reaction constant typical of the interaction: diffusion constant in case osmosis,
            depletion constant in case of depletion, injection rate in case of injection
        :param ext_conc: external concentration of the chemical species,
            only used in case of osmosis
        :return: None
        :raise AssertionError: if the interaction type is not listed in EI_TYPES or if intConstant and extConc are not float
        """
        
        assert (
            all(x == None or (type(x) == float and (x > 0 or isclose(x, 0))) for x in {int_constant, ext_conc})),\
                f"{int_constant} or {ext_conc} is not a positive or null real number"
        self.ch_species_name = sp_name
        assert int_type in Env.EI_TYPES, f"Type {int_type} is not a valid external interaction"
        self.int_type = int_type
        self.int_constant = int_constant
        self.ext_conc = ext_conc
        self.key = self.int_type+"_"+self.ch_species_name
    

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.ch_species_name != other.ch_species_name or self.int_type != other.int_type:
            return False
        return False


    def __hash__(self):
        return hash(self.key)
    

    def __str__(self, verbose:bool=False) -> str:
        out = ""
        if verbose:
            out += f"Interaction {self.key}: "
        if self.int_type == Env.EI_IN:
            if verbose:
                out += f"injection of {self.ch_species_name} at the rate of {self.int_constant} per second"
            else:
                out += f">\t{self.ch_species_name}\t;\t{self.int_constant}"
        elif self.int_type == Env.EI_OUT:
            if verbose:
                out += f"depletion of {self.ch_species_name} with reaction constant {self.int_constant}"
            else:
                out += f"{self.ch_species_name}\t>\t;\t{self.int_constant}"
        elif self.int_type == Env.EI_OSM:
            if verbose:
                out += f"osmosis of {self.ch_species_name} with diffusion constant {self.int_constant} and external concentration {self.ext_conc}"
            else:
                out += f"{self.ext_conc}\t>\t{self.ch_species_name}\t;\t{self.int_constant}"
        return out
    

    def to_string(self, verbose:bool=False) -> str:
        """Get a string representation"""

        return self.__str__(verbose)