from utils.utils import *

class Generator:
    def __init__(self, debug):
        self.debug = debug
        self.parameters = {'innerRadius': 0, 'outerRadius': 0, 'selectionProbability': 0}

    def setParameters(self, parameters):
        self.parameters = parameters

    def setParameter(self, key, value):
        self.parameters[key] = value

    def getParameters(self):
        return self.parameters
    
    def getParameter(self, key):
        return self.parameters[key]

    def initialization(self, innerRadius, outerRadius, selectionProbability):
        self.setParameter('innerRadius', innerRadius)
        self.setParameter('outerRadius', outerRadius)
        self.setParameter('selectionProbability', selectionProbability)

    def generateSpecies(self, species):
        newSpecies = []
        for s in species:
            if len(s)>self.getParameter('outerRadius'):
                continue
            elif len(s)<=self.getParameter('innerRadius'):
                newSpecies.append(s)
            elif random.random()<self.getParameter('selectionProbability'):
                newSpecies.append(s)
        return newSpecies