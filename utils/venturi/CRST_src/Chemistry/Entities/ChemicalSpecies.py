import Environment as Env

from math import isclose


class ChemicalSpecies:
    """
    Class representing a chemical species in the CRS
    """


    def __init__(self, name:str, alpha:float, quantity:float=Env.DEF_SP_QNT) -> None:
        """
        :param name: the chemical species name
        :param quantity: the chemical species quantity in the system
        :param alpha: the alpha coefficient
        :return: None
        :raise AssertionError: if quantity and alpha are nor None nor float
        """

        errMsg = f"error while creating chemical species {name}: "
        assert (
            all(x == None or (type(x) == float and (x > 0 or isclose(x, 0)))
            for x in {quantity, alpha})),\
                errMsg+f"{quantity} or {alpha} is not a positive or null real number"
        self.name = name
        self.quantity = quantity
        """the quantity of the species - and not the concentration - in the CRS"""
        self.alpha = alpha
        """coefficient describing interaction with the container, if present"""
    

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.name != other.name:
            return False
        return True
    

    def __hash__(self):
        return hash(self.name)


    def __str__(self, end:str="", verbose:bool=False) -> str:
        out = ""
        if verbose:
            out += f"Species {self.name}: quantity {self.quantity}, alpha coefficient {self.alpha}"+end
        else:
            out += f"{self.name}\t{self.quantity}\t{self.alpha}"+end
        return out


    def to_string(self, end:str="", verbose:bool=False) -> str:
        """
        Get a string representation

        :param end: the string ending the representation
        :param verbose: enables verbose output
        """

        return self.__str__(end, verbose)
        
        