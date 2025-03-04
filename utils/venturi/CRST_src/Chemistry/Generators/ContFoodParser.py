import Environment as Env

from .AChemistryParser import AChemistryParser


class ContFoodParser(AChemistryParser):
    """
    Class for parsing containers-foods files
    
    The syntax for complete chemistry files is explained in the file "chimica_spiegazione.txt";
    the syntax for containers-foods files is straightforward: in a single line there must be at maximum one chemical species name
    which acts as food or container (the containers are always in the first lines, like in the chemistry files)
    """


    def choose_production(self, tokens:list[tuple[str,str]]) -> str|None:
        """
        Choose a production according to containers-foods file syntax
        
        :param tokens: list of tokens, which are couples (token_definition, value)
        :return: the production chosen, which is recorded in Chem.PARSERPRODUCTIONS, or None if no suitable production was found
        """

        production = None
        if tokens[0][0] == Env.CT_SP:
            production = Env.PR_SCFS_DEF
        return production
        