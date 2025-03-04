import Environment as Env

from Chemistry.Entities.ChemicalSpecies import ChemicalSpecies
from Chemistry.Entities.ExtInteraction import ExtInteraction
from Chemistry.Entities.Reaction import Reaction

from abc import ABC, abstractmethod
from logging import getLogger
import re


class AChemistryParser(ABC):
    """
    Abstract class for parsing chemistry files
    The concrete classes should implement the syntax of the specific chemistry file type in the chooseProduction abstract method
    """


    LOGGER = getLogger(__name__)


    def parse_line(self, line:str, line_index:int) -> ChemicalSpecies|Reaction|ExtInteraction|None:
        """
        Parse the input line according to a specific syntax and return a new entity to be inserted in the CRS
        
        :param line: the line to be parsed
        :param line_index: index of line in the input file
        :return: new entity or None if the parsing fails due to the input file
        """
        
        err_msg = f"A parsing error occurred at line {line_index}"
        self.LOGGER.info("Parsing line '%s'", line)
        tokens = []
        # every word is separated by an empty space
        words = line.split()
        for word in words:
            # get a token corresponding to the word
            new_tok = self.tokenize(word)
            if new_tok == None:
                self.LOGGER.error(err_msg+f". Cannot tokenize {word}")
                return None
            tokens.append(new_tok)
            self.LOGGER.info(f"Token {new_tok}")
        # from a single line a new entity has to be produced according to three possibile production rules described in the environment
        new_entity = None
        production = self.choose_production(tokens)
        if production == None:
            self.LOGGER.error(err_msg+". Couldn't find a suitable production")
        else:
            new_entity = self.produce(production, tokens)
        if new_entity != None:
            self.LOGGER.info (f"New entity created: {new_entity.to_string()}")
        else:
            self.LOGGER.error(err_msg)
        return new_entity


    @abstractmethod
    def choose_production(self, tokens:list[tuple[str,str]]) -> str|None:
        """
        Choose a production according to the specific chemistry syntax, which is embodied by the chosen class
        
        :param tokens: list of tokens, which are couples (token_definition, value)
        :return: the production chosen, which is recorded in Chem.PARSERPRODUCTIONS, or None if no suitable production was found
        """

        pass

    
    def tokenize(self, word:str) -> tuple[str,str]|None:
        """
        Get a token from a word and return it

        :param word: the word to be tokenized
        :return: a new token, which is a couple (token_definition, value) where value is a string can represent a variety of things,
            or None if the tokenization fails
        """

        token = None
        val = None
        # try to apply all the token definitions in the environment, starting from the first in the dictionary
        for token_def in Env.TOKENS.items():
            if token_def[0] in {Env.CT_NUMB, Env.CT_SP}:
                rx = re.compile(token_def[1])
                match = rx.match(word)
                if match != None:
                    val = match.group(0)
            else:
                if word == token_def[1]:
                    val = word
            if val == None:
                continue
            token = (token_def[0], val)
            return token

    
    def produce(self, production:str, tokens:list[tuple[str,str]]) -> ChemicalSpecies|Reaction|ExtInteraction|None:
        """
        Apply the specified production to the list of tokens, returning a new entity of the CRS

        :param production: parser production attempted, must be listed in Chem.PARSERPRODUCTIONS
        :param tokens: list of tokens
        :return: new entity, or None if the production fails or if any of the casts to float fails
        """

        # standard error message for any issue encountered during production rule application
        err_msg = f"failed to apply {production}"
        new_entity = None

        # Chemical species definition
        if production == Env.PR_S_DEF:
            if len(tokens) != 3 or tokens[1][0] != Env.CT_NUMB or tokens[2][0] != Env.CT_NUMB:
                self.LOGGER.error(err_msg)
                return None
            sp_name = tokens[0][1]
            try:
                quantity = float(tokens[1][1])
                alpha = float(tokens[2][1])
            except ValueError:
                self.LOGGER.exception("Cast to float failed")
                return None
            try:
                new_entity = ChemicalSpecies(sp_name, alpha=alpha, quantity=quantity)
            except AssertionError:
                self.LOGGER.exception(err_msg+". Couldn't create new entity")
        
        # External interaction definition
        elif production == Env.PR_EI:
            sp_name = None
            int_type = None
            int_constant = None
            ext_conc = Env.DEF_OSM_ECONC
            if len(tokens) not in {4,5}:
                self.LOGGER.error(err_msg)
                return None
            if tokens[0][0] == Env.CT_SP:
                int_type = Env.EI_OUT
                sp_name = tokens[0][1]
                if tokens[1][0] != Env.CT_DIR or tokens[2][0] != Env.CT_HIATUS or tokens[3][0] != Env.CT_NUMB:
                    self.LOGGER.error(err_msg)
                    return None
                try:
                    int_constant = float(tokens[3][1])
                except ValueError:
                    self.LOGGER.exception("Cast to float failed")
                    return None
            elif tokens[0][0] == Env.CT_DIR:
                int_type = Env.EI_IN
                if tokens[1][0] != Env.CT_SP or tokens[2][0] != Env.CT_HIATUS or tokens[3][0] != Env.CT_NUMB:
                    self.LOGGER.error(err_msg)
                    return None
                sp_name = tokens[1][1]
                try:
                    int_constant = float(tokens[3][1])
                except ValueError:
                    self.LOGGER.exception("Cast to float failed")
                    return None
            elif tokens[0][0] == Env.CT_NUMB:
                int_type = Env.EI_OSM
                if tokens[1][0] != Env.CT_DIR or tokens[2][0] != Env.CT_SP or tokens[3][0] != Env.CT_HIATUS \
                    or tokens[4][0] != Env.CT_NUMB:
                    self.LOGGER.error(err_msg)
                    return None
                sp_name = tokens[2][1]
                try:
                    ext_conc = float(tokens[0][1])
                    int_constant = float(tokens[4][1])
                except ValueError:
                    self.LOGGER.exception("Cast to float failed")
                    return None
            else:
                self.LOGGER.error(err_msg)
                return None
            try:
                new_entity = ExtInteraction(sp_name, int_type, int_constant, ext_conc)
            except AssertionError:
                self.LOGGER.exception(err_msg+". Couldn't create new entity")
        
        # Reaction definition
        elif production == Env.PR_REACT:
            reagents = []
            products = []
            kinetic_const = float(0)
            if len(tokens) < 5 or tokens[-2][0] != Env.CT_HIATUS:
                self.LOGGER.error(err_msg)
                return None
            # process reagents and products
            first_prod_index = self._parse_semi_reaction(tokens, reagents, Env.CT_DIR)
            if first_prod_index == -1:
                self.LOGGER.error(err_msg)
                return None
            last_prod_index = first_prod_index + self._parse_semi_reaction(tokens[first_prod_index:], products, Env.CT_HIATUS)
            if last_prod_index == -1:
                self.LOGGER.error(err_msg)
                return None
            err_msg += f"An error occurred while processing reagents and products, kinetic constant expected in position {len(tokens)-1}"\
                      + f"instead it was found a {tokens[last_prod_index][0]} in position {last_prod_index}"
            if last_prod_index != len(tokens)-1 or tokens[last_prod_index][0] != Env.CT_NUMB:
                self.LOGGER.error(err_msg)
                return None
            try:
                kinetic_const = float(tokens[last_prod_index][1])
            except ValueError:
                self.LOGGER.exception("Cast to float failed")
                return None
            try:
                new_entity = Reaction(reagents, products, kinetic_const)
            except (AssertionError, ValueError):
                self.LOGGER.exception(err_msg+". Couldn't create new entity")
        
        # Simple container-food species definition
        elif production == Env.PR_SCFS_DEF:
            if len(tokens) != 1 or tokens[0][0] != Env.CT_SP:
                self.LOGGER.error(err_msg)
                return None
            sp_name = tokens[0][1]
            quantity = Env.DEF_SP_QNT
            alpha = Env.DEF_CF_ALPHA
            try:
                new_entity = ChemicalSpecies(sp_name, alpha=alpha, quantity=quantity)
            except AssertionError:
                self.LOGGER.exception(err_msg+". Couldn't create new entity")
        
        else:
            self.LOGGER.error(err_msg+". Production requested unknown")
        
        return new_entity


    
    def _parse_semi_reaction(self, tokens:list[tuple[str,str]], species_list:list[str], separator:str) -> int:
        """
        Auxiliary private function to parse a semireaction:
        either reagents or products, which are separated by an addition token, are added to the species list,
        until a suitable sepator (direction or hiatus) is found

        :param tokens: a list of tokens that should represent chemical species, additions or separations
        :param species_list: pre-existing list of chemical species names
        :param separator: separator token expected to finish the semireaction (Chem.CT_DIR or Chem.CT_HIATUS)
        :return: the index of the token following the separator, value -1 if the tokens expected to be chemical species
            are not, or if the separator token found is not the one specified as parameter
        """

        index = 0
        while(True):
            # tokens are processed in couples, starting from index 0 of the token list
            # the first must be a species name
            if tokens[index][0] != Env.CT_SP:
                self.LOGGER.error(f"Current token {tokens[index][0]} is not a chemical species")
                return -1
            species_list.append(tokens[index][1])
            index += 2
            # the second token of the couple must be either an addition or a separator
            curr_connector = tokens[index-1][0]
            if curr_connector != Env.CT_ADD:
                # if it is a separator, the semireaxction has been processed and the method can finish
                if curr_connector == separator:
                    break
                else:
                    self.LOGGER.error(f"Connector {curr_connector} is not the expected separator {separator}")
                    return -1
        return index
            