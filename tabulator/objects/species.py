from utils.utils import *

class Species:

    def __init__(self, name):
        self.name = name
        self.length = None
        self.totalProducts = None
        self.condensationProducts = None
        self.cleavageProducts = None
        self.totalCatalyzers = None
        self.condenstationCatalyzers = None
        self.cleavageCatalyzers = None
        self.speciesAsReactar = None
        self.catalyzers = []

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setLength(self):
        self.length = len(self.getName())

    def getLength(self):
        return self.length

    def setTotalProducts(self, reactions):
        totalProducts,condensationProducts,cleavageProducts = 0, 0, 0
        for r in reactions:
            splitted = r.split('>')
            reactants = cleanReaction(splitted[0])
            products = cleanReaction(splitted[1])
            for product in products:
                if product == self.getName() and product not in reactants:
                    totalProducts += 1
                    if len(reactants) == 3:
                        condensationProducts += 1
                    else:
                        cleavageProducts += 1
        self.totalProducts = totalProducts
        self.setCondensationProducts(condensationProducts)
        self.setCleavageProducts(cleavageProducts)
    
    def getTotalProducts(self):
        return self.totalProducts
    
    def setCondensationProducts(self, condensationProducts):
        self.condensationProducts = condensationProducts
    
    def getCondensationProducts(self):
        return self.condensationProducts
    
    def setCleavageProducts(self, cleavageProducts):
        self.cleavageProducts = cleavageProducts

    def getCleavageProducts(self):
        return self.cleavageProducts
    
    def setTotalCatalyzers(self, reactions):
        condensationCatalyzers,cleavageCatalyzers = 0, 0
        catalysts = []
        for r in reactions:
            splitted = r.split('>')
            reactants = cleanReaction(splitted[0])
            products = cleanReaction(splitted[1])
            for reactant in reactants:
                if reactant in products:
                    catalyst = reactant
            for product in products:
                if product == self.getName() and product not in reactants:
                    if catalyst not in catalysts:
                        catalysts.append(catalyst)
                        if len(reactants) == 3:
                            condensationCatalyzers += 1
                        else:
                            cleavageCatalyzers += 1
        self.totalCatalyzers = len(catalysts)
        self.setCatalyzers(catalysts)
        self.setCondensationCatalyzers(condensationCatalyzers)
        self.setCleavageCatalyzers(cleavageCatalyzers)

    def getTotalCatalyzers(self):
        return self.totalCatalyzers

    def setCondensationCatalyzers(self, condensationCatalyzers):
        self.condensationCatalyzers = condensationCatalyzers

    def getCondensationCatalyzers(self):
        return self.condensationCatalyzers
    
    def setCleavageCatalyzers(self, cleavageCatalyzers):
        self.cleavageCatalyzers = cleavageCatalyzers

    def getCleavageCatalyzers(self):
        return self.cleavageCatalyzers
    
    def setSpeciesAsReactar(self, reactions):
        speciesAsReactar = 0
        for r in reactions:
            splitted = r.split('>')
            reactants = cleanReaction(splitted[0])
            for reactant in reactants:
                if reactant == self.getName():
                    speciesAsReactar += 1
        self.speciesAsReactar = speciesAsReactar

    def getSpeciesAsReactar(self):
        return self.speciesAsReactar
    
    def setCatalyzers(self, catalyzers):
        self.catalyzers = catalyzers

    def getCatalyzers(self):
        if not self.catalyzers:
            return "None"
        else:
            out=''
            for s in self.catalyzers:
                out+=s+','
            return out[:-1]
