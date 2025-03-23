from utils.utils import BASE_DIR, writeOnExcelFile, cleanReaction, orderSpecies, printTabulatedCatalysts, printTabulatedSpecies
from utils.parser import getRules, getObjects
from tabulator.objects.catalyst import Catalyst
from tabulator.objects.species import Species

class Tabulator():

    def __init__(self, debug):
        self.debug = debug
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
        if self.debug:
            printTabulatedSpecies(self.getSpecies())

    def getSpecies(self):
        return self.species

    def setReactions(self):
        self.reactions = getObjects(BASE_DIR)[1]

    def getReactions(self):
        return self.reactions
    
    def getCatatlysts(self):
        return self.catalysts
    
    def sortCatalysts(self):
        self.catalysts=orderSpecies(self.getCatatlysts())
    
    def addCatalyst(self, catalyst):
        self.catalysts.append(catalyst)

    def setRules(self):
        rules = getRules(BASE_DIR)
        if rules:
            self.rules = rules
        else:
            self.rules = []

    def getRules(self):
        return self.rules
    
    def initialize(self):
        self.setReactions()
        self.setRules()
        self.setCatalysts()
        self.setSpecies()
    
    def catalystsList(self, rules, reactions):
        catalysts = []
        if not rules:
            for r in reactions:
                splitted = r.split('>')
                reactants = cleanReaction(splitted[0])
                products = cleanReaction(splitted[1])
                for reactant in reactants:
                    if reactant in products and reactant not in catalysts:
                        catalysts.append(reactant)
            return catalysts
        else:
            for r in rules:
                if r.getCatalyst() not in catalysts:
                    catalysts.append(r.getCatalyst())
            return catalysts
    
    def setCatalysts(self):
        catalysts = self.catalystsList(self.getRules(), self.getReactions())
        if self.getRules():
            for c in catalysts:
                catalyst = Catalyst(c)
                catalyst.setLength(c)
                catalyst.setTotalRules(self.getRules())
                catalyst.setTotalReactions(self.getReactions())
                catalyst.setCatalyzerAsReagent(self.getReactions())
                catalyst.setCatalyzedSpecies(self.getReactions())
                self.addCatalyst(catalyst)
        else:
            for c in catalysts:
                catalyst = Catalyst(c)
                catalyst.setLength(c)
                catalyst.setTotalReactions(self.getReactions())
                catalyst.setCatalyzerAsReagent(self.getReactions())
                catalyst.setCatalyzedSpecies(self.getReactions())
                self.addCatalyst(catalyst)
        self.sortCatalysts()
        if self.debug:
            printTabulatedCatalysts(self.getCatatlysts())

    def writeFile(self):
        try:
            writeOnExcelFile(self.getCatatlysts(), self.getSpecies())
        except PermissionError:
            print(f"ERRORE! Il file è già aperto in Excel. Chiudilo e riprova.")

    
