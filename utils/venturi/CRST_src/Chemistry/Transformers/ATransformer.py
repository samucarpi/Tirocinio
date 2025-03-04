from Chemistry.Entities.ACRS import ACRS

from abc import ABC, abstractmethod
from copy import copy
from logging import getLogger


class ATransformer(ABC):
    """
    Abstract class to build a deeply transformed version of a starting Chemical Reaction System (CRS)
    """


    LOGGER = getLogger(__name__)
    

    def __init__(self, transforming_CRS:ACRS) -> None:
        """
        Initializer

        The original transforming CRS is copied, so it is not actually modified by the class
        :param transforming_CRS: the CRS undergoing transformation
        :return: None
        """
        
        self._CRS = copy(transforming_CRS)
    

    @abstractmethod
    def transform(self) -> ACRS|None:
        """
        Tranform the CRS into a new one with specific properties
        
        :return: the new transformed CRS if the process is successfull, None otherwise
        """
        pass

