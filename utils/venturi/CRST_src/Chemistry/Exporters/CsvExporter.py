import Environment as Env

from .AExporter import AExporter
from .Log import Log
from pandas import DataFrame


class CsvExporter(AExporter):
    """
    Class defining methods to export a chemistry object to .csv format
    """


    def _init_supported_classes(self) -> None:
        """
        Define the supported classes

        In order to support csv exporting, the class must implement a get_data() method returning the data as a dictionary,
        iterable, tuple or a Pandas Dataframe
        """
        self.supported_classes = {Log}


    def _init_write_data(self) -> None:
        self.data = self.obj.get_data()
        self.mode = "w"
        self.extension = Env.FMT_CSV


    def _write(self, file) -> None:
        df = DataFrame(self.data, dtype="object") 
        df.to_csv(file, index=False)
    