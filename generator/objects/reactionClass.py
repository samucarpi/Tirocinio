
from utils.utils import calculateRandomValue

class ReactionClass():
    def __init__(self, catalyst, start, end):
        self.reagents = []
        self.catalyst = catalyst
        self.start = start
        self.end = end
        self.split = None
    
    def setReagents(self, reagents):
        self.reagents = reagents
    
    def getReagents(self):
        return self.reagents
    
    def addReagent(self, reagent):
        self.reagents.append(reagent)
    
    def setCatalyst(self, catalyst):
        self.catalyst = catalyst

    def getCatalyst(self):
        return self.catalyst
    
    def setStart(self, start):
        self.start = start
    
    def getStart(self):
        return self.start
    
    def setEnd(self, end):
        self.end = end
    
    def getEnd(self):
        return self.end
    
    def setSplit(self, split):
        self.split = split
    
    def getSplit(self):
        return self.split
    
    def calculateSplit(self, activesite):
        self.setSplit(calculateRandomValue(0, len(activesite)))
        while self.getSplit() == 0 or self.getSplit() == len(activesite):
            self.setSplit(calculateRandomValue(0, len(activesite)))
    
    def complementaryActivesite(self, activesite, monomers):
        complementary = ""
        for c in activesite:
            for m in monomers:
                if c == m["name"]:
                    complementary += m["complementary"]
        return complementary
    
class CleavageReactionClass(ReactionClass):
    def __init__(self, catalyst, start, end):
        super().__init__(catalyst, start, end)
    
    def cleave(self, monomers):
        catalyst = self.getCatalyst().getName()
        activesite = catalyst[self.getStart():self.getEnd()]
        activesite = self.complementaryActivesite(activesite, monomers)
        self.calculateSplit(activesite)
        self.addReagent(activesite)
    
class CondensationReactionClass(ReactionClass):
    def __init__(self, catalyst, start, end):
        super().__init__(catalyst, start, end)
    
    def condense(self, monomers):
        catalyst = self.getCatalyst().getName()
        activesite = catalyst[self.getStart():self.getEnd()]
        activesite = self.complementaryActivesite(activesite, monomers)
        self.calculateSplit(activesite)
        reagent1=activesite[:self.getSplit()]
        reagent2=activesite[self.getSplit():]
        self.addReagent(reagent1)
        self.addReagent(reagent2)

