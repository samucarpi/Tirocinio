
from .species import Species

class Catalyst(Species):
    def __init__(self, name, isInitial):
        super().__init__(name, isInitial)
        self.isCondensation = False
        self.isCleavage = False
        self

    def setIsCondensation(self, isCondensation):
        self.isCondensation = isCondensation
    
    def getIsCondensation(self):
        return self.isCondensation
    
    def setIsCleavage(self, isCleavage):
        self.isCleavage = isCleavage

    def getIsCleavage(self):
        return self.isCleavage