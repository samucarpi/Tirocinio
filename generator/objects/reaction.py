
class Reaction():
    def __init__(self, reactionClass):
        self.reactants = []
        self.products = []
        self.reactionClass = reactionClass
        self.multiplicity = 1

    def setReactants(self, reactants):
        self.reactants = reactants
    
    def getReactants(self):
        return self.reactants
    
    def addReactant(self, reactant):
        self.reactants.append(reactant)

    def setProducts(self, products):
        self.products = products
    
    def getProducts(self):
        return self.products
    
    def addProduct(self, product):
        self.products.append(product)
    
    def getReactionClass(self):
        return self.reactionClass
    
    def setReactionClass(self, reactionClass):
        self.reactionClass = reactionClass

    def setMultiplicity(self, multiplicity):
        self.multiplicity = multiplicity

    def getMultiplicity(self):
        return self.multiplicity
    
    def printReaction(self):
        if self.getReactionClass().getCatalyst().getIsCleavage():
            return self.getReactants()[0]+" + "+self.getReactants()[1]+" --> "+self.getProducts()[0]+" + "+self.getProducts()[1]+" + "+self.getProducts()[2]
        else:
            return self.getReactants()[0]+" + "+self.getReactants()[1]+" + "+self.getReactants()[2]+" --> "+self.getProducts()[0]+" + "+self.getProducts()[1]
        