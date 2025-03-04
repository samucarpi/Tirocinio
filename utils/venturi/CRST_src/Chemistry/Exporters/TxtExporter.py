import Environment as Env

from .AExporter import AExporter
from .Log import Log
from Chemistry.Entities.ACRS import ACRS


class TxtExporter(AExporter):
    """
    Class defining methods to export a chemistry object to .txt format
    """


    def _init_supported_classes(self) -> None:
        self.supported_classes = {ACRS, Log}


    def _init_write_data(self) -> None:
        self.data = self.obj.to_string()
        self.mode = "w"
        self.extension = Env.FMT_TXT


    def _write(self, file) -> None:
        print(self.data, file=file)
    