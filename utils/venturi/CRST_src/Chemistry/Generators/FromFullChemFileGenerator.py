import Environment as Env

from .AFileGenerator import AFileGenerator
from .FullChemistryParser import FullChemistryParser
from Chemistry.Entities.ChemicalSpecies import ChemicalSpecies
from Chemistry.Entities.Chemostat import Chemostat
from Chemistry.Entities.ExtInteraction import ExtInteraction
from Chemistry.Entities.Protocell import Protocell
from Chemistry.Entities.Reaction import Reaction


class FromFullChemFileGenerator(AFileGenerator):
    """
    Class defining generation methods of a Chemical Reaction System (CRS) starting from a full-chemistry file
    """


    def _collect_elements(self) -> bool:
        """
        Collect the basic constituents of a CRS from the specified full-chemistry file

        :return: True if the operation succeeds, False otherwise
        """

        errMsg = f"Failed to load CRS from file {self.filename}: "
        self.LOGGER.info("Starting CRS generation")

        parser = FullChemistryParser()
        try:
            with open(self.filename, "r") as file:
                self.LOGGER.info(f"File {self.filename} opened")
                for i, line in enumerate(file.readlines()):
                    line = line.strip()
                    if line == "":
                        continue
                    # parse a line, creating a new entity of the system
                    entity = parser.parse_line(line, i)
                    # if the parsing fails, the file doesn't follow the requested syntax
                    if entity == None:
                        errMsg += f"complete chemistry syntax not respected at line {i}:{line}"
                        raise ValueError
                    # assign the entity to its category in the CRS
                    # the entity can either be a chemical species definition, an interaction with the external enviroment,
                    # or a reaction
                    # the first Chem.CRS_NCONT lines of the file must specify containers
                    if i < Env.CRS_NCONT:
                        if not isinstance(entity, ChemicalSpecies):
                            errMsg += f"the first {Env.CRS_NCONT} lines must represent containers"
                            raise ValueError
                        self._containers.append(entity)
                    elif isinstance(entity, ChemicalSpecies):
                        self._reacting_ch_species.append(entity)
                    elif isinstance(entity, Reaction):
                        self._reactions.append(entity)
                    elif isinstance(entity, ExtInteraction):
                        self._ext_interactions.append(entity)
                    else:
                        errMsg += "unrecognized entity"
                        raise ValueError
        except OSError:
            self.LOGGER.exception(errMsg+f"couldn't open file {self.filename}")
            return False
        except ValueError:
            self.LOGGER.error(errMsg)
            return False
        return True


    def _define_set_class(self) -> bool:
        """
        Define the new CRS type from collected external interactions and set the correspondant private attribute

        :return: True if the operation succeeds, False otherwise
        """

        # deduce the CRS type from collected external interactions:
        # injection/depletion are characteristic of a chemostat, instead osmosis is present in protocells;
        # a coherent system cannot mix osmosis with injections/depletions, so all external interactions collected are checked
        if len(self._ext_interactions) == 0:
            self.LOGGER.error("No external interactions defined, impossible to deduce CRS type")
            return False
        if all(x.int_type == Env.EI_OSM for x in self._ext_interactions):
            system_type = Protocell
        elif all(x.int_type in {Env.EI_IN, Env.EI_OUT} for x in self._ext_interactions):
            system_type = Chemostat
        else:
            self.LOGGER.error("Impossible to deduce CRS type from defined external interactions")
            return False
        self.LOGGER.info(f"System of type {system_type.get_type_string()} detected")
        self._type = system_type
        return True


    def _add_components(self) -> bool:
        """
        Add all the basic constituents collected to the new CRS, creating its components

        :return: True if the operation succeeds, False otherwise
        """
         
        out_ext_interactions = [ext_int for ext_int in self._ext_interactions if ext_int.int_type == Env.EI_OUT]
        food_ext_interactions = [ext_int for ext_int in self._ext_interactions if ext_int.int_type in {Env.EI_OSM, Env.EI_IN}]

        for container in self._containers:
            if not self._CRS.add_container(container):
                self.LOGGER.error(f"Chemical species {container} cannot be added as container to the CRS")
                return False
            self.LOGGER.info(f"Chemical species {container} added as container to the CRS")
        for ch_species in self._reacting_ch_species:
            out_ext_int = None
            for ext_int in out_ext_interactions:
                if ext_int.ch_species_name == ch_species.name:
                    out_ext_int = ext_int
                    break
            addOK = self._CRS.add_ch_species(ch_species) if out_ext_int == None else self._CRS.add_ch_species(ch_species, out_ext_int)
            if not addOK:
                self.LOGGER.error(f"Chemical species {ch_species.name} cannot be added to the CRS")
                return False
            self.LOGGER.info(f"Chemical species {ch_species.name} added to the CRS")
            if out_ext_int != None:
                self._ext_interactions.remove(out_ext_int)
                self.LOGGER.info(f"Depletion {out_ext_int.key} added to the CRS")
        for reaction in self._reactions:
            if not self._CRS.add_reaction(reaction):
                self.LOGGER.error(f"Reaction {reaction.key} is not valid for the CRS")
                return False
            self.LOGGER.info(f"Reaction {reaction.key} added to the CRS")
        for ext_int in food_ext_interactions:
            self._ext_interactions.remove(ext_int)
            food = ext_int.ch_species_name
            if not self._CRS.set_as_food(food, ext_int):
                self.LOGGER.error(f"Chemical species {food} with interaction {ext_int.key} cannot be set as food for the CRS")
                return False
            self.LOGGER.info(f"Chemical species {food} set as food for the system, with interaction {ext_int.key}")
        return True
