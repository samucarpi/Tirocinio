from .BaseIntegrityValidator import BaseIntegrityValidator


class NullIntegrityValidator(BaseIntegrityValidator):
    """
    CRS integrity validator that performs no checks
    """

    def validate(self) -> bool:
        """
        Validate the system

        No checks are performed

        :return: True
        """
        
        self.LOGGER.warning("CRS integrity checks are disabled by configuration")
        return True