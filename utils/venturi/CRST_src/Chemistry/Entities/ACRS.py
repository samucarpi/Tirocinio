import Environment as Env

from .ChemicalSpecies import ChemicalSpecies
from .ExtInteraction import ExtInteraction
from .Reaction import Reaction

from abc import ABC, abstractmethod
from logging import getLogger
from math import isclose


class ACRS(ABC):
    """
    Abstract class defining a generic Chemical Reaction System (CRS)
    """


    LOGGER = getLogger(__name__)


    def __init__(self) -> None:
        """
        Initializer

        To be called by builder classes contained in the package "Generators", it only initialized the basic data structure as empty
        sets and dictionaries
        :return: None
        """

        self._ch_species = {}
        """
        Dictionary of all chemical species, associates chemical species names as keys to ChemicalSpecies objects
        """
        self._containers = set()
        """
        Set of container species names,
            they must be valid keys in the dictionary of all chemical species
        """
        self._ext_interactions = {}
        """
        Dictionary of ExtInteraction objects representing interactions with the external environment,
            associates externat interactions keys with their entitites
        """
        self._foods = set()
        """
        Set of chemical species names acting as food:
            in case of protocell they are the species that can permeate through the membrane,
            in case of chemostat they are the species that are actively injected;
            they must be valid keys in the dictionary of all chemical species and need to have the corresponding external
            interaction(s) set in the dictionary of all external interactions
        """
        self._reactions = {}
        """
        The reactions that can take place in the system,
            represented as dictionary associating the key of the Reaction objects to objects themselves
        """
        self._catalysts = set()
        """
        Set of the catalysts of the reactions,
            represented as a set of couples (chemical_species_name, reaction_key);
            the reaction keys must be valid keys in the dictionary of all reactions
        """

        self._reactions_count = {}
        """Dictionary counting the reactions present in the system"""
        self._reactions_count["Total"] = 0
    

    def update_reaction_count(self):
        """Update the reaction count attribute"""

        # initialize the dictionary
        for reaction_type in Env.R_TYPES:
            self._reactions_count[reaction_type] = 0
        self._reactions_count["Total"] = len(self._reactions)

        for reaction in self._reactions.values():
            self._reactions_count[reaction.type] = self._reactions_count.get(reaction.type, 0) + 1
    

    def __copy__(self):
        CRStype = type(self)
        newCRS = CRStype()
        newCRS._containers = self._containers.copy()
        newCRS._ch_species = self._ch_species.copy()
        newCRS._foods = self._foods.copy()
        newCRS._reactions = self._reactions.copy()
        newCRS._catalysts = self._catalysts.copy()
        newCRS._ext_interactions = self._ext_interactions.copy()
        newCRS._reactions_count = self._reactions_count.copy()
        return newCRS


    def __str__(self, verbose:bool=False) -> str:
        out = ""
        if verbose:
            out += f"\nChemical Reaction System (CRS)\nType: {self.get_type_string()}\n\nContainers:\n"
        for containerName in self._containers:
            container = self._ch_species.get(containerName)
            out += container.to_string(verbose=verbose)+"\n"
        if verbose:
            out += "\nChemical species:\n"
        for ch_species in self._ch_species.values():
            if not ch_species.name in self._containers:
                out += ch_species.to_string(verbose=verbose)+"\n"
        if verbose:
            out += "\nFood: "
            for foodName in self._foods:
                out += foodName+" "
        out += "\n"
        if verbose:
            out += "\nReactions:\n"
        for reaction in self._reactions.values():
            out += reaction.to_string(verbose=verbose)+"\n"
        if verbose:
            out += "\nReactions count:\n"
            for reaction_type_and_number in self._reactions_count.items():
                out += f"{reaction_type_and_number[0]} {reaction_type_and_number[1]}, "
            out += "\n\nCatalysts:\n"
            for catalyst in self._catalysts:
                out += f"{catalyst[0]} catalyzes reaction {catalyst[1]}\n"
            out += "\nExternal interactions:\n"
        for ext_int in self._ext_interactions.values():
            out += ext_int.to_string(verbose=verbose)+"\n"
        if verbose:
            out += "\n"
        return out
    

    def to_string(self, verbose:bool=False) -> str:
        """Get a string representation"""
        return self.__str__(verbose)
    

    @classmethod
    @abstractmethod
    def get_type_string(cls) -> str:
        """Get the string representing the type of CRS"""
        pass
    
    
    def get_all_species_names(self) -> list[str]:
        """Get a list of all chemical species names"""
        return [ch_species.name for ch_species in self._ch_species.values()]
    

    def get_containers_names(self) -> list[str]:
        """Get a list of containers names"""
        return [container for container in self._containers]
    

    def get_foods_names(self) -> list[str]:
        """Get a list of food names"""
        return [food for food in self._foods]


    def get_reactive_species_names(self, no_food:bool=False) -> list[str]:
        """
        Get a list of reactive species names

        :param no_food: True if food species are excluded by the list
        :return: list of strings
        """

        # TODO add configurations settings to consider foods and containers reactive or not
        names = []
        for ch_species_name in self._ch_species:
            if (
                ch_species_name in self._containers
                or (no_food and ch_species_name in self._foods)):
                    continue
            names.append(ch_species_name)
        return names
    

    def get_all_reactions(self) -> list[Reaction]:
        """Get a list of all the reactions in the system"""
        return [reaction for reaction in self._reactions.values()]
    

    def get_all_ext_interactions(self) -> list[ExtInteraction]:
        """Get a list of all the external interactions in the system"""
        return [extInt for extInt in self._ext_interactions.values()]

    
    def get_all_catalyses(self) -> list[tuple[str, str]]:
        """Get a list of all the catalyses, as couples of strings wich are the catalyst and reaction keys"""
        return [cat for cat in self._catalysts]


    def get_chemical_species(self, name:str) -> ChemicalSpecies|None:
        """Get the chemical species with the specified name"""
        return self._ch_species.get(name, None)
    

    def get_reaction(self, key:str) -> Reaction|None:
        """Get the reaction with the specified key"""
        return self._reactions.get(key, None)
    

    def get_ext_interaction(self, key:str) -> ExtInteraction|None:
        """Get the external interaction with the specified key"""
        return self._ext_interactions.get(key, None)
    

    def get_reaction_count(self, react_type:str = "Total") -> int:
        """
        Get the number of reactions of the type specified

        :param react_type: the type of reaction, needs to part of Env.R_TYPES;
            if the type is not present in the dictionary, returns 0; if the type is not specified, returns the total reactions
        :return: the number of reactions
        """
        return self._reactions_count.get(react_type, 0)

        
    def get_interacting_species_names(self, req_ext_int:str) -> list[str]:
        """
        Get a list of species interacting with the environment as specifed
        
        Used by the validation method
        :param req_ext_int: the requested type of external interaction,
            it must be a string specified in Env.EI_TYPES, otherwise the method returns an empty list
        :return: the list of species that have the requested external interaction type
        """

        names = []
        if req_ext_int not in Env.EI_TYPES:
            return names

        for ext_int in self._ext_interactions.values():
            if ext_int.int_type == req_ext_int:
                names.append(ext_int.ch_species_name)
        return names
    
    
    @abstractmethod
    def add_ch_species(self, ch_species:ChemicalSpecies) -> bool:
        """
        Tries to add a chemical species to the system

        :param ch_species: the chemical species to be added
        :return: True if the addition is successful, False otherwise
        """
        pass
        

    def add_container(self, container:ChemicalSpecies) -> bool:
        """
        Tries to add a chemical species as container to the system

        :param container: the chemical species to be added as container
        :return: True if the operation is successful, False otherwise
        """

        if container.name in self._ch_species:
            return False

        # TODO add a check to consider the fact that the container could be reactive
        if not isclose(container.alpha, 0):
            return False
        
        self._ch_species[container.name] = container
        self._containers.add(container.name)
        self.LOGGER.info(f"Container {container} added to the system")
        return True
    

    @abstractmethod
    def set_as_food(self, food_name:str, ext_int:ExtInteraction=None) -> bool:
        """
        Tries to set an existing chemical species as food for the system, also setting the correspondant external interaction

        The type of interaction added depends on the system type;
        needs to call the private _setFoodWithDefinedInt method
        :param food_name: the chemical species name to be set as food
        :param ext_int: the external interactions to be set, must be coherent with the food chosen and the system type;
            if it is not specified, a default interaction is added
        :return: True if the operation is successful, False otherwise
        """
        pass
    

    def _set_food_with_defined_int(self, food:str, ext_int:ExtInteraction, needed_int_type:str) -> bool:
        """
        Auxiliary private method used by set_as_food

        :param food: the chemical species name to be set as food
        :param ext_int: the external interactions to be set, must be coherent with the food chosen and the system type
        :param needed_int_type: the interactions type needed for the specific system
        :return: True if the operation is successful, False otherwise
        """

        ch_species = self._ch_species.get(food, None)
        if ch_species == None or food in self._containers or food in self._foods:
            return False
        
        # TODO add a configuration to decide if food should interact with the membrane
        if not isclose(ch_species.alpha, 0):
            return False
        
        if not ext_int.int_type == needed_int_type or not ext_int.ch_species_name == food:
            return False
        if ext_int.key in self._ext_interactions:
            return False
            
        self._foods.add(food)
        self.LOGGER.info(f"Food {food} added to the system")
        self._ext_interactions[ext_int.key] = ext_int
        self.LOGGER.info(f"External interaction {ext_int.key} added to the system")

        return True


    def add_reaction(self, reaction:Reaction) -> bool:
        """
        Tries to add a reaction to the system

        :param reaction: the specific reaction to be added
        :return: True if the addition is successful, False otherwise
        """

        # check if the reaction specified is already present
        if reaction.key in self._reactions:
            return False

        # check if the reaction is valid
        if not (all(x in self.get_reactive_species_names() \
                for x in reaction.get_all_species_names())):
            return False
        if reaction.type not in Env.R_TYPES:
            return False
        
        # add the reaction, the catalyses and update the reaction count dictionary
        self._reactions[reaction.key] = reaction
        for catalystName in reaction.catalysts:
            self._catalysts.add((catalystName, reaction.key))
        self._reactions_count[reaction.type] = self._reactions_count.get(reaction.type, 0) + 1
        self._reactions_count["Total"] += 1

        return True
    

    def delete_ch_species(self, ch_species_name:str) -> bool:
        """
        Tries to delete a chemical species from the system, and all its associated external interactions and reactions

        A container species cannot be removed
        :param ch_species_name: the chemical species name
        :return: True if the deletion is successful, False otherwise
        """
        
        ch_species = self._ch_species.get(ch_species_name, None)
        if ch_species == None:
            self.LOGGER.info(f"Chemical species {ch_species_name} not found")
            return False
        
        if ch_species_name in self._containers:
            self.LOGGER.info(f"Chemical species {ch_species_name} cannot be removed: it is a container")
            return False
        
        if ch_species_name in self._foods:
            self._foods.remove(ch_species_name)
            self.LOGGER.info(f"Chemical species {ch_species_name} removed from food set")

        for extInt in [x for x in self._ext_interactions.values()]:
            if extInt.ch_species_name == ch_species_name:
                del self._ext_interactions[extInt.key]
                self.LOGGER.info(f"External interaction {extInt.key} removed")
        
        for reaction in [x for x in self._reactions.values()]:
            if ch_species_name in reaction.get_all_species_names():
                # return value not checked since the presence in the dictionary is checked earlier
                self.delete_reaction(reaction.key)
        
        del self._ch_species[ch_species_name]
        self.LOGGER.info(f"Chemical species {ch_species_name} removed from the system")

        return True

    
    def delete_reaction(self, reaction_key:str) -> bool:
        """
        Tries to delete a chemical species from the system, and all its associated external interactions and reactions

        :param reaction_key: the reaction key
        :return: True if the deletion is successful, False otherwise
        """

        reaction = self._reactions.get(reaction_key, None)
        if reaction == None:
            self.LOGGER.info(f"Reaction {reaction_key} not found")
            return False
        
        for catalystName in reaction.catalysts:
            self._catalysts.discard((catalystName, reaction_key))
            self.LOGGER.info(f"Catalyses {(catalystName, reaction_key)} removed")

        del self._reactions[reaction_key]
        self.LOGGER.info(f"Reaction {reaction_key} removed from the system")
        self._reactions_count[reaction.type] = self._reactions_count.get(reaction.type) - 1
        self._reactions_count["Total"] -= 1

        return True