from abc import ABC, abstractmethod
from datetime import datetime
from io import TextIOWrapper
from typing import Any

import os
import string


class AExporter (ABC):
    """
    Abstract class defining methods to export a chemistry object to a variety of formats
    """


    def __init__(self, obj:Any, output_folder_path:str, create_folder:bool=False) -> None:
        """
        Initializer

        :param obj: the object to be exported
        :param output_folder_path: the output folder path name
        :param create_folder: create the outpput folder if it doesn't exist, by default the initializer doesn't try
            folder creation, so the folder should already exist
        :return: None
        :raise ValueError: if the object is not writable
        :raise IsADirectoryError: if the already existing output folder indicated is not a directory
        :raise OSError: if the folder creation fails
        """

        self.supported_classes = {}
        self._init_supported_classes()
        if all(not isinstance(obj, sup_class) for sup_class in self.supported_classes):
            raise ValueError(f"Class {type(obj)} not supported")
        self.obj = obj
        if create_folder:
            # try to create the output folder requested
            if not os.path.exists(output_folder_path):
                try:
                    os.mkdir(output_folder_path)
                except OSError:
                    raise OSError("Folder creation failed")
        if not os.path.isdir(output_folder_path):
            raise IsADirectoryError(f"Output folder path {output_folder_path} is not a directory")
        self.output_folder_path = output_folder_path
        self.output_file_path = ""
        self.timestamp = AExporter.get_timestamp()
        self.data = None
        self.mode = ""
        self.extension = ""
        self._init_write_data()


    @abstractmethod
    def _init_supported_classes(self) -> None:
        """
        Initialize the supported classes
        """
        pass


    @abstractmethod
    def _init_write_data(self) -> None:
        """
        Initialize the following data structures used for the write process:
        - object data to be written
        - write mode
        - extension for the output file
        """
        pass


    def export(self, prefix:str="", suffix:str="") -> str:
        """
        Export a CRS to a specific format

        :param prefix: additional information to insert as prefix into the file name
        :param suffix: additional information to insert as suffix into the file name
        :return: the operation log
        :raise IOError:
        :raise OSError:
        :raise FileNotFoundError:
        :raise PermissionError:
        """

        object_type = type(self.obj).__name__
        output_file_name = f"{prefix}{object_type}{self.timestamp}{suffix}.{self.extension}"
        output_file_path = os.path.join(self.output_folder_path, output_file_name)

        with open(output_file_path, self.mode) as file:
            self._write(file)
        
        return f"{object_type} successfully exported to {output_file_path}"


    @abstractmethod
    def _write(self, file:TextIOWrapper) -> None:
        """
        Writes to the output file
        
        :file: the file to be written
        :return: None
        :raise IOError:
        :raise OSError:
        """
        pass
    

    @staticmethod
    def get_timestamp() -> str:
        """
        Get a a unique timestamp for export purposes

        The method can be called on the class, in order to use the timestamp outside the current scope
        :return: a timestamp representing the current instant in time
        """
        
        now = str(datetime.today())
        # remove punctuation and spaces
        return now.translate(str.maketrans("", "", string.punctuation+string.whitespace))