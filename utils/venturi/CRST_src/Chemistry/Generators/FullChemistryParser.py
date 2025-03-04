import Environment as Env

from .AChemistryParser import AChemistryParser


class FullChemistryParser(AChemistryParser):
    """
    Class for parsing complete chemistry files
    
    The syntax for complete chemistry files is explained in the file "chimica_spiegazione.txt";
    """


    def choose_production(self, tokens:list[tuple[str,str]]) -> str|None:
        """
        Choose a production according to full chemistry file syntax
        
        :param tokens: list of tokens, which are couples (token_definition, value)
        :return: the production chosen, which is recorded in Chem.PARSERPRODUCTIONS, or None if no suitable production was found
        """

        production = None
        # parsing algorithm: choose the production rule based on the first tokens
        if tokens[0][0] == Env.CT_DIR:
            production = Env.PR_EI
        elif tokens[0][0] == Env.CT_NUMB:
            production = Env.PR_EI
        elif tokens[0][0] == Env.CT_SP:
            if tokens[1][0] == Env.CT_NUMB:
                production = Env.PR_S_DEF
            elif tokens[1][0] == Env.CT_ADD:
                production = Env.PR_REACT
            elif tokens[1][0] == Env.CT_DIR:
                if  tokens[2][0] == Env.CT_SP:
                    production = Env.PR_REACT
                elif  tokens[2][0] == Env.CT_HIATUS:
                    production = Env.PR_EI
        return production
    