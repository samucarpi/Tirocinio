
class Reaction():
    def __init__(self):
        self.reactants = []
        self.products = []
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

    def setMultiplicity(self, multiplicity):
        self.multiplicity = multiplicity

    def getMultiplicity(self):
        return self.multiplicity
    
    def setCatalyst(self, catalyst):
        self.catalyst = catalyst
    
    def getCatalyst(self):
        return self.catalyst
    
    def printReaction(self):
        if self.getCatalyst().getIsCleavage():
            return self.getReactants()[0].getName()+" + "+self.getCatalyst().getName()+" --> "+self.getProducts()[0].getName()+" + "+self.getProducts()[1].getName()+" + "+self.getCatalyst().getName()
        else:
            return self.getReactants()[0].getName()+" + "+self.getReactants()[1].getName()+" + "+self.getCatalyst().getName()+" --> "+self.getProducts()[0].getName()+" + "+self.getCatalyst().getName()
        