
from .species import Species

class Catalyst(Species):
    def __init__(self, name):
        super().__init__(name)
        self.isCondensation = False
        self.isCleavage = False

    def setIsCondensation(self, isCondensation):
        self.isCondensation = isCondensation
    
    def getIsCondensation(self):
        return self.isCondensation
    
    def setIsCleavage(self, isCleavage):
        self.isCleavage = isCleavage

    def getIsCleavage(self):
        return self.isCleavage