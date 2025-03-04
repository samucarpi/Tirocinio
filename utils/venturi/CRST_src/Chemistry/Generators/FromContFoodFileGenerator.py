import Environment as Env

from .AFileGenerator import AFileGenerator
from .ContFoodParser import ContFoodParser
from Chemistry.Entities.ChemicalSpecies import ChemicalSpecies
from Chemistry.Entities.ACRS import ACRS
from Chemistry.Validators.BaseIntegrityValidator import BaseIntegrityValidator


class FromContFoodFileGenerator(AFileGenerator):
    """
    Class defining generation methods of a Chemical Reaction System (CRS) starting from a containers-foods file
    """


    def __init__(self, validator:BaseIntegrityValidator, filename:str, system_class:ACRS) -> None:
        """
        Initializer

        :param validator: the CRS integrity validator
        :param filename: the file used for generation
        :param system_class: class of CRS, must be a valid subclass of ACRS
            this parameter must be passed via the services builder, which ensures the correctness of the class
        :return: None
        :raise FileExistsError: if the the filename doesn't exixst
        """

        super().__init__(validator, filename)
        self._type = system_class


    def _collect_elements(self) -> bool:
        """
        Collect the basic constituents of a CRS, from the specified containers-foods file

        :return: True if the operation succeeds, False otherwise
        """

        errMsg = f"Failed to load CRS from file {self.filename}: "
        self.LOGGER.info("Starting CRS generation")

        parser = ContFoodParser()
        try:
            with open(self.filename, "r") as file:
                self.LOGGER.info(f"File {self.filename} opened")
                for i, line in enumerate(file.readlines()):
                    line = line.strip()
                    if line == "":
                        continue
                    new_species = parser.parse_line(line, i)
                    if new_species == None or not isinstance(new_species, ChemicalSpecies):
                        errMsg += f"containers-foods syntax not respected at line {i}:{line}"
                        raise ValueError
                    # the first Chem.CRS_NCONT lines of the file specify containers, the others are foods
                    if i < Env.CRS_NCONT:
                        new_species.quantity = Env.DEF_C_QNT
                        new_species.alpha = Env.DEF_CF_ALPHA
                        self._containers.append(new_species)
                    else:
                        new_species.quantity = Env.DEF_F_QNT
                        new_species.alpha = Env.DEF_CF_ALPHA
                        self._reacting_ch_species.append(new_species)
        except OSError:
            self.LOGGER.exception(errMsg+f"couldn't open file {self.filename}")
            return False
        except ValueError:
            self.LOGGER.error(errMsg)
            return False
        return True
    

    def _define_set_class(self) -> bool:
        """
        Nothing specific has to be done, since the set class is requested via config

        :return: True
        """

        return True


    def _add_components(self) -> bool:
        """
        Add all the basic constituents collected to the new CRS, creating its components

        :return: True if the operation succeeds, False otherwise
        """
        
        for container in self._containers:
            if not self._CRS.add_container(container):
                self.LOGGER.error(f"Chemical species {container.name} cannot be added as container for the CRS")
                return False
            self.LOGGER.info(f"Chemical species {container.name} added as container to the CRS")
        for ch_species in self._reacting_ch_species:
            if not self._CRS.add_ch_species(ch_species):
                self.LOGGER.error(f"Chemical species {ch_species.name} cannot be added to the CRS")
                return False
            self.LOGGER.info(f"Chemical species {ch_species.name} added to the CRS")
            if not self._CRS.set_as_food(ch_species.name):
                self.LOGGER.error(f"Chemical species {ch_species.name} cannot be set as food for the CRS")
                return False
            self.LOGGER.info(f"Chemical species {ch_species.name} set as food for the CRS")
        return True
    
