import Environment as Env

from .BaseIntegrityValidator import BaseIntegrityValidator


class FormulaIntegrityValidator(BaseIntegrityValidator):
    """
    CRS integrity validator that performs checks encompassing reactions formulas
    """
    

    def validate(self) -> bool:
        """
        Validate the system

        Additional checks on reaction formulas are enforced

        :return: True if the system is validated, False ohterwise
        """
        
        if not super().validate():
            return False

        # each reaction reagents must be in the correct order, depending on reaction type
        for reaction in self.CRS.get_all_reactions():
            # cleavages need to respect this kind of formula (catalysts excluded): AAB -> A + AB
            if reaction.type == Env.R_CLEAVE:
                if len(reaction.reagents) != 1 or len(reaction.products) != 2:
                    self.LOGGER.error(f"Reaction {reaction.key} doesn't represent a proper cleave")
                    return False
                if reaction.reagents[0] != reaction.products[0]+reaction.products[1]:
                    self.LOGGER.error(f"Reaction {reaction.key} doesn't represent a proper cleave")
                    return False
            # condensations need to respect this kind of formula (catalysts excluded): A + AB -> AAB
            elif reaction.type == Env.R_COND:
                if len(reaction.reagents) != 2 or len(reaction.products) != 1:
                    self.LOGGER.error(f"Reaction {reaction.key} doesn't represent a proper condensation")
                    return False
                if reaction.reagents[0]+reaction.reagents[1] != reaction.products[0]:
                    self.LOGGER.error(f"Reaction {reaction.key} doesn't represent a proper condensation")
                    return False
            # exchanges need to have 2 reagents and products and have the same individual elements at the two sides of the reaction
            elif reaction.type == Env.R_EXCH:
                if len(reaction.reagents) != 2 or len(reaction.products) != 2:
                    self.LOGGER.error(f"Reaction {reaction.key} doesn't represent a proper exchange")
                    return False
                reag_comp = sorted([x for x in reaction.reagents[0]+reaction.reagents[1]])
                prod_comp = sorted([x for x in reaction.products[0]+reaction.products[1]])
                if reag_comp != prod_comp:
                    self.LOGGER.error(f"Reaction {reaction.key} doesn't represent a proper exchange")
                    return False
    
        return True