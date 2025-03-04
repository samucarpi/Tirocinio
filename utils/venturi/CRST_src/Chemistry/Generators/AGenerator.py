from Chemistry.Entities.ACRS import ACRS
from Chemistry.Validators.BaseIntegrityValidator import BaseIntegrityValidator

from abc import ABC, abstractmethod
from logging import getLogger


class AGenerator(ABC):
    """
    Abstract class defining generation methods of a Chemical Reaction System (CRS)
    """


    LOGGER = getLogger(__name__)


    def __init__(self, validator:BaseIntegrityValidator) -> None:
        """
        Initializer

        :param validator: the CRS integrity validator
        """

        self._CRS = None
        self._containers = []
        self._reacting_ch_species = []
        self._reactions = []
        self._ext_interactions = []
        self._type = None
        self._validator = validator


    def create(self) -> ACRS|None:
        """
        Create a CRS starting from some knowledge
        
        :return: the concrete CRS constructed, None if construction fails
        """

        steps = [self._collect_elements, self._define_set_class, self._create_CRS, self._add_components, self._finalize]
        for step in steps:
            if not step():
                self.LOGGER.error(f"CRS creation failed at step {step.__name__}")
                return None
        return self._CRS

    
    @abstractmethod
    def _collect_elements(self) -> bool:
        """
        Collect the basic constituents of a CRS,
        which are all the chemical species, the containers, the reactions and the external interactions

        :return: True if the operation succeeds, False otherwise
        """
        pass
    

    @abstractmethod
    def _define_set_class(self) -> bool:
        """
        Define the new CRS class (if not known) and set the correspondant private attribute

        :return: True if the operation succeeds, False otherwise
        """
        pass


    def _create_CRS(self) -> bool:
        """
        Create a basic instance of a CRS

        :return: True if the operation succeeds, False otherwise
        """
       
        self._CRS = self._type()
        return True


    @abstractmethod
    def _add_components(self) -> bool:
        """
        Add all the basic constituents collected to the new CRS, creating its components

        :return: True if the operation succeeds, False otherwise
        """
        pass


    def _finalize(self) -> bool:
        """
        Finalize CRS creation, validating the system and updating the reaction count

        :return: True if finalization succeedes, False otherwise
        """

        self._validator.calibrate(self._CRS)
        if not self._validator.validate():
            self.LOGGER.error("Created CRS failed to validate")
            return False
        self._CRS.update_reaction_count()
        return True
