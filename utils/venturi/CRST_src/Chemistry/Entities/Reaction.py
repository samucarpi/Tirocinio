import Environment as Env


class Reaction:
    """
    Class describing a reaction of the CRS
    """


    def __init__(self, reagents:list[str], products:list[str], kinetic_const:float=Env.DEF_REACT_K) -> None:
        """
        Initializer

        :param reagents: list of reagents names
        :param products: list of product names
        :param kinetic_const: kinetic constant of the reaction
        :return: None
        :raise AssertionError: if kineticConst is not float
        :raise ValueError: if reaction is not validated
        """

        assert type(kinetic_const) == float
        self.reagents = reagents
        """list of reagent names"""
        self.products = products
        """list of product names"""
        self.kinetic_const = kinetic_const
        """kinetic constant"""
        self.catalysts = []
        """list of catalysts names"""
        # remove catalysts from the reagents and products lists, starting from the end, and add them to the catalysts list
        self.reagents.reverse()
        self.products.reverse()
        reagents_list = self.reagents.copy()
        for reagent in reagents_list:
            n_occ_reag = self.reagents.count(reagent)
            n_occ_prod = self.products.count(reagent)
            if n_occ_reag > 0 and n_occ_prod > 0:
                for _ in range(min(n_occ_reag,n_occ_prod)):
                    # remove one occurrence of the catalyst from back of the reagents and products lists
                    # and add it to the reaction catalysts list
                    self.reagents.remove(reagent)
                    self.products.remove(reagent)
                    self.catalysts.append(reagent)
        self.reagents.reverse()
        self.products.reverse()
        # reaction type determination
        if len(reagents) < len(products):
            self.type = Env.R_CLEAVE
        elif len(reagents) > len(products):
            self.type = Env.R_COND
        else:
            self.type = Env.R_EXCH
        # the reaction formula with catalysts specififed and with reagents and products sorted alphabetically is a unique key
        # it was dediced however to not use the sort option to allow the specification of chemistries where order is important
        self.key = self.get_formula(sort=False, with_cat=True)
    
    
    def get_formula(self, sort:bool=False, with_cat:bool=True) -> str:
        """Get the reaction formula

        The formula is essentially a list of all the reagents and products of the reaction
        :param sort: True if the lists of reagents and products should be sorted alphabetically to guarantee unicity
        :param with_cat: True if a list of the catalysts follows the products
        :return: a string representing the reaction formula
        """

        func = lambda x: sorted(x) if sort else x
        reagents = func(self.reagents)
        products = func(self.products)
        catalysts = sorted(self.catalysts)

        formula = "+".join(reagents)
        formula += ">"
        formula += "+".join(products)
        if with_cat:
            formula += "_"
            formula += "+".join(catalysts)
        return formula


    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.key != other.key:
                return False
        return True


    def __hash__(self):
        return hash(self.key)


    def __str__(self, verbose:bool=False) -> str:
        out = ""
        reagents = self.reagents.copy()
        products = self.products.copy()
        if verbose:
            out += f"{self.type} reaction {self.key}:\t"
        else:
            reagents.extend(self.catalysts)
            products.extend(self.catalysts)
        for i, reagent in enumerate(reagents):
            if i == 0:
                out += f"{reagent}"
            else:
                out += f"\t{Env.TOKENS.get(Env.CT_ADD)}\t{reagent}"
        out += f"\t{Env.TOKENS.get(Env.CT_DIR)}\t"
        for i, product in enumerate(products):
            if i == 0:
                out += f"{product}"
            else:
                out += f"\t{Env.TOKENS.get(Env.CT_ADD)}\t{product}"
        if verbose:
            out += "\n\tcatalysts"
            for catalyst in set(self.catalysts):
                out += f" {catalyst}"
            out += ", kinetic constant "
        else:
            out += "\t;\t"
        out += f"{self.kinetic_const}"
        return out

    
    def to_string(self, verbose:bool=False) -> str:
        """Get a string representation"""

        return self.__str__(verbose)
    

    def get_all_species_names(self) -> list[str]:
        """
        Get a list of all the chemical species names involved in the reaction
        
        :return: list of all the chemical species names involved in the reaction
        """

        all_species = self.reagents+self.products+self.catalysts
        return all_species