from .AGenerator import AGenerator
from Chemistry.Validators.BaseIntegrityValidator import BaseIntegrityValidator

import os.path


class AFileGenerator(AGenerator):
    """
    Abstract class defining generation methods of a Chemical Reaction System (CRS) from information contained in a file
    """


    def __init__(self, vaidator:BaseIntegrityValidator, filename:str) -> None:
        """
        Initializer
        
        :param validator: the CRS integrity validator
        :param filename: the file used for generation
        :return: None
        :raise FileExistsError: if the the filename doesn't exixst
        """

        super().__init__(vaidator)
        if not os.path.exists(filename):
            raise FileExistsError(f"File {filename} not present")
        self.filename = filename

