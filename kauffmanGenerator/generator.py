from utils.utils import *
from utils.parser import *
from kauffmanGenerator.objects.species import *
from kauffmanGenerator.objects.catalyst import *
from kauffmanGenerator.objects.reaction import *

class Generator:

    def __init__(self, debug):
        self.debug = debug
        self.seed = None
        self.parameters = {}
        self.species = []
        self.reactions = []
        self.catalyzer = []

    def setSeed(self, seed):
        seed = generateSeed(seed)
        self.seed = seed

    def getSeed(self):
        return self.seed
    
    def setParameters(self, parameters):
        self.parameters = parameters

    def getParameters(self):
        return self.parameters
    
    def getParameter(self,name):
        parameters= self.getParameters()
        return parameters[name]
    
    def setSpecies(self, species):
        self.species = species

    def getSpecies(self):
        return self.species
    
    def addReaction(self, reaction):
        self.reactions.append(reaction)

    def getReactions(self):
        return self.reactions
    
    def initializeSpecies(self):
        file = open(KAUFFMAN_GENERATOR_SPECIES_FILE, 'w')
        species = monomerCombinations(self.getParameter("monomers"), self.getParameter("maxProductLength"))
        file.write("\n".join(species))
        file.close()
        species = [newSpecies(s,kauffman=True) for s in species]
        self.setSpecies(species)

    def initializeParameters(self):
        error,parameters = getKauffmanGeneratorParameters(KAUFFMAN_GENERATOR_PARAMETERS_FILE)
        if error:
            for message in parameters:
                print(colored(message,"red",attrs=['bold']))
        else:
            self.setParameters(parameters)
    
    def initialization(self):
        self.initializeParameters()
        self.initializeSpecies()

    def getCatalyst(self, species):
        species = random.choice(species)
        catalyst = Catalyst(species.getName())
        if calculateProbability(self.getParameter('probabilityOfCleavage')):
            catalyst.setIsCleavage(True)
        else:
            catalyst.setIsCondensation(True)
        return catalyst
    
    def cleave(self, species, catalyst):
        reaction = Reaction()
        reaction.setCatalyst(catalyst)
        reagent = random.choice(species)
        reaction.addReactant(reagent)
        split = random.randint(1,len(reagent)-1)
        product1Name = reagent.getName()[:split]
        product2Name = reagent.getName()[split:]
        product1 = [s for s in species if s.getName() == product1Name]
        product2 = [s for s in species if s.getName() == product2Name]
        reaction.addProduct(product1[0])
        reaction.addProduct(product2[0])
        return reaction
    
    def condense(self, species, catalyst):
        reaction = Reaction()
        reaction.setCatalyst(catalyst)
        reagent1 = random.choice(species)
        while len(reagent1.getName()) > self.getParameter("maxProductLength")-1:
            reagent1 = random.choice(species)
        reagent2 = random.choice(species)
        while len(reagent1.getName()) + len(reagent2.getName()) > self.getParameter("maxProductLength"):
            reagent2 = random.choice(species)
        reaction.addReactant(reagent1)
        reaction.addReactant(reagent2)
        productName = reagent1.getName()+reagent2.getName()
        product = [s for s in species if s.getName() == productName]
        reaction.addProduct(product[0])
        return reaction
        
    def generate(self, species, reactionsLimit):
        reactionsCount = 0
        while reactionsCount < 2:
            catalyst = self.getCatalyst(species)
            while len(catalyst.getName()) < self.getParameter("lowerLimitForCatalyst"):
                catalyst = self.getCatalyst(species)
            if catalyst.getIsCleavage():
                reaction=self.cleave(species, catalyst)
            else:
                reaction=self.condense(species, catalyst)
            self.addReaction(reaction)
            reactionsCount += 1
            

    def reaction(self):
        species=self.getSpecies()
        reactionsLimit=self.getParameter("maxReactionProduced")
        self.generate(species, reactionsLimit)
        print([reaction.printReaction() for reaction in self.getReactions()])
        