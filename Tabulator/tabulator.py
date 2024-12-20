from Utils.utils import BASE_DIR, writeOnExcelFile
from Utils.parser import getRules, getObjects
from .objects.catalyst import Catalyst
from .objects.species import Species

class Tabulator():

    def __init__(self):
        self.species = []
        self.reactions = []
        self.catalysts = []
        self.rules = []

    def addSpecies(self, species):
        self.species.append(species)

    def setSpecies(self):
        reactions = self.getReactions()
        species = getObjects(BASE_DIR)[0]
        for s in species:
            s = Species(s)
            s.setLength()
            s.setTotalProducts(reactions)
            s.setTotalCatalyzers(self.getReactions())
            s.setSpeciesAsReactar(self.getReactions())
            self.addSpecies(s)
        self.printSpecies()

    def printSpecies(self):
        for s in self.getSpecies():
            print(s.getName(), s.getLength(), s.getTotalProducts(), s.getCondensationProducts(), s.getCleavageProducts(), s.getTotalCatalyzers(), s.getCondensationCatalyzers(), s.getCleavageCatalyzers(), s.getCatalyzers(), s.getSpeciesAsReactar())

    def getSpecies(self):
        return self.species

    def setReactions(self):
        self.reactions = getObjects(BASE_DIR)[1]

    def getReactions(self):
        return self.reactions
    
    def setCatatlysts(self, catalysts):
        self.catalysts = catalysts
    
    def getCatatlysts(self):
        return self.catalysts
    
    def addCatalyst(self, catalyst):
        self.catalysts.append(catalyst)

    def setRules(self):
        self.rules = getRules(BASE_DIR)

    def getRules(self):
        return self.rules
    
    def initialize(self):
        self.setReactions()
        self.setRules()
        self.setCatalysts()
        self.setSpecies()
    
    def catalystsList(self, rules):
        catalysts = []
        for r in rules:
            if r.getCatalyst() not in catalysts:
                catalysts.append(r.getCatalyst())
        return catalysts
    
    def setCatalysts(self):
        catalysts = self.catalystsList(self.getRules())
        for c in catalysts:
            catalyst = Catalyst(c)
            catalyst.setLength(c)
            catalyst.setTotalRules(self.getRules())
            catalyst.setTotalReactions(self.getReactions())
            catalyst.setCatalyzerAsReagent(self.getReactions())
            catalyst.setCatalyzedSpecies(self.getReactions())
            self.addCatalyst(catalyst)
        self.printCatalysts()
        
    def printCatalysts(self):
        for c in self.getCatatlysts():
            print(c.getName(), c.getLength(), c.getTotalRules(), c.getCondensationRules(), c.getCleavageRules(), c.getTotalReactions(), c.getCondensationReactions(), c.getCleavageReactions(), c.getCatalyzerAsReagent(), c.getNumberOfCatalyzedSpecies(), c.getCatalyzedSpecies())

    def writeFile(self):
        writeOnExcelFile(self.getCatatlysts(), self.getSpecies())

    
