import Environment as Env

from .ATransformer import ATransformer
from Chemistry.Entities.ACRS import ACRS
from Chemistry.Entities.ChemicalSpecies import ChemicalSpecies
from itertools import product
from random import choice, randrange
from logging import getLogger


class Censor(ATransformer):
    """
    Class to build a modifified version of a Chemical Reaction System (CRS) with more chemical species
    """


    LOGGER = getLogger(__name__)
    

    def __init__(self, transforming_CRS:ACRS, alphabet:str, max_name_length:int=Env.DEF_SP_NLEN) -> None:
        """
        Initializer

        :param transforming_CRS: the CRS undergoing transformation
        :param alphabet: the alphabet
        :param max_name_length: maximum length of the species names
        :return: None
        """
        super().__init__(transforming_CRS)
        self._alphabet = alphabet
        self.max_name_length = max_name_length
        self.target_species_number = None
        self._set_max_n_species()


    def _set_max_n_species(self) -> None:
        """
        Private method to set the attribute max_n_species, which represents maximum number of species that the original CRS can contain

        :return: None
        """

        max_n_species = 0
        for i in range(self.max_name_length):
            max_n_species += len(self._alphabet)**(i+1)
        # check if the containers have names that could be assigned to random chemical species
        for container_name in self._CRS.get_containers_names():
            has_not_r_generatable_name = False
            for letter in container_name:
                if letter not in self._alphabet:
                    has_not_r_generatable_name = True
                    break
            # if the name is not random generatable increase the maximum number of chemical species by 1
            if has_not_r_generatable_name:
                max_n_species += 1
        if max_n_species > Env.MAX_N_SPECIES:
            max_n_species = Env.MAX_N_SPECIES
        self.max_n_species = max_n_species


    def set_target_species_number(self, req_species_number:int=0) -> None:
        """
        Set the target species number

        :param req_species_number: number of total species required;
            if the value is 0, the object aims to build a new CRS with the maximum number of species allowed by the max name length
        """

        self.target_species_number = req_species_number
        if not len(self._CRS.get_all_species_names()) < self.target_species_number <= self.max_n_species:
            if self.target_species_number != 0:
                self.LOGGER.warning(f"Number of species requested {self.target_species_number} is not valid, defaulting to {self.max_n_species}")
            else:
                self.LOGGER.info(f"Defaulting to {self.max_n_species} species")
            self.target_species_number = self.max_n_species


    def transform(self) -> ACRS|None:
        """
        Expand the dictionary of chemical species of the CRS, adding chemical species randomly or sistematically

        :return: the new transformed CRS if the process is successfull, None otherwise
            Currently no ways for the tranformation process to fail
        """

        # check that the set target species number function has been called
        if self.target_species_number == None:
            self.set_target_species_number(0)

        existing_species_names = self._CRS.get_all_species_names()
        if len(existing_species_names) == self.target_species_number:
            self.LOGGER.info(f"The starting CRS already has the target species number {self.target_species_number}")
            return self._CRS
        
        self.LOGGER.info(
            f"Creating an inert {self._CRS.get_type_string()} with {self.target_species_number} species, "
            f"with maximum name length of {self.max_name_length}")
        ch_species_names = []
        # if all possibile chemical species have to be added, define their names sistematically
        if (self.target_species_number == self.max_n_species):
            for name_length in range(1,self.max_name_length+1):
                for comb in product(self._alphabet,repeat=name_length):
                    new_species_name = "".join(comb[_] for _ in range(name_length))
                    if not new_species_name in existing_species_names:
                        ch_species_names.append(new_species_name)
        # else define their names randomically and then order them
        else:
            while (len(ch_species_names) + len(existing_species_names) < self.target_species_number):
                name_length = randrange(self.max_name_length)+1
                new_species_name="".join(choice(self._alphabet) for _ in range(name_length))
                # ensure to create unique names
                if new_species_name in ch_species_names or new_species_name in existing_species_names:
                    continue
                ch_species_names.append(new_species_name)
            # sort the new names in dictionary order and then by length
            ch_species_names.sort()
            ch_species_names.sort(key=len)

        # create all the new chemical species
        for new_species_name in ch_species_names:
            if self._CRS.get_type_string() == Env.CRS_PTC:
                alpha=Env.DEF_PTC_SP_ALPHA
            elif self._CRS.get_type_string() == Env.CRS_CSTR:
                alpha=Env.DEF_CSTR_SP_ALPHA
            new_species = ChemicalSpecies(new_species_name, alpha=alpha)
            self._CRS.add_ch_species(new_species)
            self.LOGGER.info(f"New species created: {new_species.to_string()}")
        
        return self._CRS
    