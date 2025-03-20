
class Reaction():
    def __init__(self, reactionClass):
        self.reactants = []
        self.products = []
        self.reactionClass = reactionClass
        self.catalyst = None
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
    
    def setCatalyst(self, catalyst):
        self.catalyst = catalyst
    
    def getCatalyst(self):
        return self.catalyst
    
    def printReaction(self, kauffman=False):
        if kauffman:
            if self.getCatalyst().getIsCleavage():
                return self.getReactants()[0].getName()+" + "+self.getCatalyst().getName()+" > "+self.getProducts()[0].getName()+" + "+self.getProducts()[1].getName()+" + "+self.getCatalyst().getName()
            else:
                return self.getReactants()[0].getName()+" + "+self.getReactants()[1].getName()+" + "+self.getCatalyst().getName()+" > "+self.getProducts()[0].getName()+" + "+self.getCatalyst().getName()
        else:
            if self.getReactionClass().getCatalyst().getIsCleavage():
                return self.getReactants()[0]+" + "+self.getReactants()[1]+" > "+self.getProducts()[0]+" + "+self.getProducts()[1]+" + "+self.getProducts()[2]
            else:
                return self.getReactants()[0]+" + "+self.getReactants()[1]+" + "+self.getReactants()[2]+" > "+self.getProducts()[0]+" + "+self.getProducts()[1]
        