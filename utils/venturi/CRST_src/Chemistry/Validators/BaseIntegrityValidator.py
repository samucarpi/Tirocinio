import Environment as Env

from Chemistry.Entities.ACRS import ACRS

from logging import getLogger
from math import isclose


class BaseIntegrityValidator():
    """
    Base CRS integrity validator, performing loose checks
    """


    LOGGER = getLogger(__name__)


    def __init__(self) -> None:
        self.CRS = None


    def calibrate(self, CRS:ACRS) -> None:
        """
        Calibrate the validator on a specific CRS

        :param CRS: the CRS to be validated
        """

        self.CRS = CRS
    

    def validate(self) -> bool:
        """
        Validate the system

        The method should be extended by child classes, to inherit the core checks performed

        :return: True if the system is validated, False ohterwise
        """
        
        if self.CRS == None:
            self.LOGGER.error("Strategy not calibrated")
            return False

        
        # the number of container species must be equal to the amount specified in the configuration
        if len(self.CRS.get_containers_names()) != Env.CRS_NCONT:
            self.LOGGER.error(f"Container species number not coheret with {Env.CRS_NCONT}")
            return False

        # container species need to be present amongst the chemical species
        for container_name in self.CRS.get_containers_names():
            ch_species = self.CRS.get_chemical_species(container_name)
            if ch_species == None:
                self.LOGGER.error(f"The container {container_name} is not present amongst the chemical species")
        
        # any species appearing in a reaction or interaction must be present amongst the chemical species
        for reaction in self.CRS.get_all_reactions():
            for ch_species_name in set(reaction.get_all_species_names()):
                if not ch_species_name in self.CRS.get_all_species_names():
                    self.LOGGER.error(f"Species {ch_species_name} is not listed amongst the chemical species")
                    return False
        for ext_int in self.CRS.get_all_ext_interactions():
            if not ext_int.ch_species_name in self.CRS.get_all_species_names():
                self.LOGGER.error(f"Species {ch_species_name} is not listed amongst the chemical species")
                return False
        
        # each reaction must have its catalysts memorized in the the catalyst set
        for reaction in self.CRS.get_all_reactions():
            for catalyst in reaction.catalysts:
                if not (catalyst, reaction.key) in self.CRS.get_all_catalyses():
                    self.LOGGER.error(f"Catalyst {(catalyst, reaction.key)} not registered")
                    return False

        # each catalyst must be a valid chemical species and associated to the correct reaction
        for catalyst, reaction_key in self.CRS.get_all_catalyses():
            if catalyst not in self.CRS.get_all_species_names():
                self.LOGGER.error(f"Catalyst {catalyst} is not present amongst the chemical species")
                return False
            reaction = self.CRS.get_reaction(reaction_key)
            if reaction == None:
                self.LOGGER.error(f"Reaction {reaction_key} catalyzed by {catalyst} is not listed amongst the reactions")
                return False
            if not catalyst in reaction.catalysts:
                self.LOGGER.error(f"Catalyst {catalyst} is not listed amongst reaction {reaction_key} catalysts")
                return False

        
        ## Protocell-specific checks
        if self.CRS.get_type_string() == Env.CRS_PTC:
            # any food species must be present amongst the chemical species and have an osmosis interaction defined
            diffusing_species = self.CRS.get_interacting_species_names(Env.EI_OSM)
            for food_name in self.CRS.get_foods_names():
                chSpecies = self.CRS.get_chemical_species(food_name)
                if chSpecies == None:
                    self.LOGGER.error(f"Food {food_name} is not present amongst the chemical species")
                    return False
                if chSpecies.name not in diffusing_species:
                    self.LOGGER.error(f"Food {food_name} doesn't diffuse through the protocell membrane")
                    return False
        
        ## Chemostat-specific checks
        elif self.CRS.get_type_string() == Env.CRS_CSTR:

            # container species need to have alpha coefficient 0 and not to be involved in reactions or interactions in any way
            for container_name in self.CRS.get_containers_names():
                ch_species = self.CRS.get_chemical_species(container_name)
                if not isclose(abs(ch_species.alpha), 0):
                    self.LOGGER.error(f"The container {ch_species.name} is influencing its own growth")
                    return False
                for reacting_species in [reaction.get_all_species_names() for reaction in self.CRS.get_all_reactions()]:
                    if ch_species in reacting_species:
                        self.LOGGER.error(f"The container {ch_species.name} is involved in a reaction")
                        return False
        
            # any food species must be present amongst the chemical species and not amongst the containers,
            # also it must have both an input and an output interaction set
            entering_species = self.CRS.get_interacting_species_names(Env.EI_IN)
            for food_name in self.CRS.get_foods_names():
                ch_species_name = self.CRS.get_chemical_species(food_name)
                if ch_species_name == None or ch_species_name.name in self.CRS.get_containers_names():
                    self.LOGGER.error(f"Food {food_name} is not present amongst the chemical species or is listed as container")
                    return False
                # only input interaction is checked, since output is checked later
                if ch_species_name.name not in entering_species:
                    self.LOGGER.error(f"Food {food_name} doesn't enter in the chemostat")
                    return False
                    
            # the alpha coefficients of the chemical species must be 0 and every chemical species has to deplete in time
            exiting_species = self.CRS.get_interacting_species_names(Env.EI_OUT)
            for ch_species_name in self.CRS.get_reactive_species_names():
                chSpecies = self.CRS.get_chemical_species(ch_species_name)
                if not isclose(abs(chSpecies.alpha), 0):
                    self.LOGGER.error(
                        f"In a chemostat no chemical species should interact with the container: issue with species {ch_species_name}")
                    return False
                if ch_species_name not in exiting_species:
                    self.LOGGER.error(
                        f"In a chemostat every chemical species needs a depletion defined: issue with species {ch_species_name}")
                    return False
            
        return True