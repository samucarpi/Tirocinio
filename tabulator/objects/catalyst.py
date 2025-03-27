from utils.utils import *

from collections import Counter

class Catalyst:

    def __init__(self, name):
        self.name = name
        self.length = None
        self.totalRules = None
        self.condensationRules = None
        self.cleavageRules = None
        self.totalReactions = None
        self.condenstationReactions = None
        self.cleavageReactions = None
        self.catalyzerAsReagent = None
        self.numberOfCatalyzedSpecies = None
        self.catalyzedSpecies = []

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setLength(self, name):
        self.length = len(name)

    def getLength(self):
        return self.length

    def setTotalRules(self, rules):
        totalRules,condensationRules,cleavageRules = 0, 0, 0
        for r in rules:
            if r.getCatalyst() == self.getName():
                totalRules += 1
                if r.getType() == 'Condensazione':
                    condensationRules += 1
                if r.getType() == 'Cleavage':
                    cleavageRules += 1
        self.totalRules = totalRules
        self.setCondensationRules(condensationRules)
        self.setCleavageRules(cleavageRules)

    def getTotalRules(self):
        return self.totalRules
    
    def setCondensationRules(self, condensationRules):
        self.condensationRules = condensationRules
    
    def getCondensationRules(self):
        return self.condensationRules
    
    def setCleavageRules(self, cleavageRules):
        self.cleavageRules = cleavageRules
    
    def getCleavageRules(self):
        return self.cleavageRules

    def setTotalReactions(self, reactions):
        totalReactions,condensationReactions,cleavageReactions = 0,0,0
        for r in reactions:
            splitted = r.split('>')
            sx = cleanReaction(splitted[0])
            dx = cleanReaction(splitted[1])
            alreadyCounted = False
            for reagent in sx:
                if reagent in dx and reagent == self.getName() and not alreadyCounted:
                    alreadyCounted = True
                    totalReactions += 1
                    if len(sx) == 3:
                        condensationReactions += 1
                    else:
                        cleavageReactions += 1
        self.totalReactions = totalReactions
        self.setCondensationReactions(condensationReactions)
        self.setCleavageReactions(cleavageReactions)

    def getTotalReactions(self):
        return self.totalReactions

    def setCondensationReactions(self, condensationReactions):
        self.condenstationReactions = condensationReactions

    def getCondensationReactions(self):
        return self.condenstationReactions

    def setCleavageReactions(self, cleavageReactions):
        self.cleavageReactions = cleavageReactions

    def getCleavageReactions(self):
        return self.cleavageReactions

    def setCatalyzerAsReagent(self, reactions):
        catalystAsReagent = 0
        for r in reactions:
            splitted = r.split('>')
            sx = cleanReaction(splitted[0])
            dx = cleanReaction(splitted[1])
            sxCount = sum(1 for reagent in sx if reagent==self.getName())
            dxCount = sum(1 for reagent in dx if reagent==self.getName())
            if sxCount-dxCount > 0:
                catalystAsReagent += 1
        self.catalyzerAsReagent = catalystAsReagent

    def getCatalyzerAsReagent(self):
        return self.catalyzerAsReagent

    def setNumberOfCatalyzedSpecies(self, numberOfCatalyzedSpecies):
        self.numberOfCatalyzedSpecies = numberOfCatalyzedSpecies
    
    def getNumberOfCatalyzedSpecies(self):
        return self.numberOfCatalyzedSpecies
    
    def setCatalyzedSpecies(self, reactions):
        species = []
        for r in reactions:
            splitted = r.split('>')
            sx = cleanReaction(splitted[0])
            dx = cleanReaction(splitted[1])
            if self.getName() in sx and self.getName() in dx:
                count_sx = Counter(sx)
                count_dx = Counter(dx)
                for specie in count_dx:
                    delta = count_dx[specie]-count_sx.get(specie, 0)
                    if delta > 0:
                        species.append(specie)
        species = list(set(species))
        self.setNumberOfCatalyzedSpecies(len(species))
        self.catalyzedSpecies = species
    
    def getCatalyzedSpecies(self):
        if not self.catalyzedSpecies:
            return "None"
        else:
            out=''
            for s in self.catalyzedSpecies:
                out+=s+','
            return out[:-1]
    
    def addCatalyzedSpecies(self, catalyzedSpecies):
        self.catalyzedSpecies.append(catalyzedSpecies)

