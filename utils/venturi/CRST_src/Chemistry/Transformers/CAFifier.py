from .ASubsetifier import ASubsetifier
from Chemistry.Entities.CAF import CAF


class CAFifier(ASubsetifier):
    """
    Class to build a RAF from a starting Chemical Reaction System (CRS) by adding reactions in steps
    """
    

    def _init_subset_class(self) -> None:
        """Initialize subset class"""
        
        self.subset_class = CAF
