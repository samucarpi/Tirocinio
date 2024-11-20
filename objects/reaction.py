
class Reaction():
    def __init__(self, reactionClass):
        self.reactants = []
        self.products = []
        self.reactionClass = reactionClass

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
