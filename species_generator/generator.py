from utils.utils import *

class Generator:
    def __init__(self, debug):
        self.debug = debug
        self.parameters = {'innerRadius': 0, 'outerRadius': 0, 'selectionProbability': 0, 'monomers': []}

    def setParameters(self, parameters):
        self.parameters = parameters

    def setParameter(self, key, value):
        self.parameters[key] = value

    def getParameters(self):
        return self.parameters
    
    def getParameter(self, key):
        return self.parameters[key]

    def initialization(self, innerRadius, outerRadius, selectionProbability, monomers):
        self.setParameter('innerRadius', innerRadius)
        self.setParameter('outerRadius', outerRadius)
        self.setParameter('selectionProbability', selectionProbability)
        self.setParameter('monomers', monomers)
        
    def generateSpecies(self):
        generatedSpecies = []
        species = monomerCombinations(self.getParameter('monomers'), self.getParameter('outerRadius'))
        for s in species:
            if len(s)<=self.getParameter('innerRadius'):
                generatedSpecies.append(s)
            elif random.random()<self.getParameter('selectionProbability'):
                generatedSpecies.append(s)
        return generatedSpecies