from utils.utils import *
from utils.parser import *
from utils.loader import *
from generator.objects.species import *
from generator.objects.catalyst import *
from generator.objects.reaction import *
import time

class Generator:

    def __init__(self, debug):
        self.debug = debug
        self.seed = None
        self.parameters = {}
        self.species = []
        self.processedSpecies = []
        self.reactions = []
        self.notFilteredReactions = []
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
    
    def addNotFilteredReactions(self, reaction):
        self.notFilteredReactions.append(reaction)

    def getNotFilteredReactions(self):
        return self.notFilteredReactions
    
    def addProcessedSpecies(self, species):
        if species not in self.getProcessedSpecies():
            self.processedSpecies.append(species)

    def getProcessedSpecies(self):
        return self.processedSpecies
    
    def sortSpecies(self):
        self.processedSpecies=orderSpecies(self.getProcessedSpecies())
    
    def initializeSpecies(self):
        file = open(KAUFFMAN_GENERATOR_SPECIES_FILE, 'w')
        species = monomerCombinations(self.getParameter("monomers"), self.getParameter("maxProductLength"))
        file.write("\n".join(species))
        file.close()
        species = [createSpeciesObject(s) for s in species]
        self.setSpecies(species)

    def initializeParameters(self):
        error,parameters = getKauffmanGeneratorParameters(KAUFFMAN_GENERATOR_PARAMETERS_FILE)
        if error:
            for message in parameters:
                print(colored(message,"red",attrs=['bold']))
            exit()
        else:
            self.setParameters(parameters)
    
    def initialization(self):
        self.initializeParameters()
        self.setSeed(self.getParameter("seed"))
        self.initializeSpecies()
        if self.debug:
            printParameters(self.getParameters(),kauffman=True)
            printSpecies(self.getSpecies(),kauffman=True)

    def createCatalyst(self, species):
        pickedSpecies = random.choice(species)
        catalyst = Catalyst(pickedSpecies.getName())
        while len(catalyst.getName()) < self.getParameter("lowerLimitForCatalyst"):
            pickedSpecies = random.choice(species)
            catalyst = Catalyst(pickedSpecies.getName())
        if calculateProbability(self.getParameter('probabilityOfCleavage')):
            catalyst.setIsCleavage(True)
        else:
            catalyst.setIsCondensation(True)
        self.addProcessedSpecies(pickedSpecies)
        return catalyst
    
    def cleave(self, species, catalyst):
        reaction = Reaction(reactionClass=None)
        reaction.setCatalyst(catalyst)
        reagent = random.choice(species)
        while len(reagent.getName()) < 2:
            reagent = random.choice(species)
        reaction.addReactant(reagent)
        self.addProcessedSpecies(reagent)
        split = random.randint(1,len(reagent.getName())-1)
        product1Name = reagent.getName()[:split]
        product2Name = reagent.getName()[split:]
        product1 = [s for s in species if s.getName() == product1Name]
        product2 = [s for s in species if s.getName() == product2Name]
        reaction.addProduct(product1[0])
        reaction.addProduct(product2[0])
        self.addProcessedSpecies(product1[0])
        self.addProcessedSpecies(product2[0])
        return reaction
    
    def condense(self, species, catalyst):
        reaction = Reaction(reactionClass=None)
        reaction.setCatalyst(catalyst)
        reagent1 = random.choice(species)
        while len(reagent1.getName()) > self.getParameter("maxProductLength")-1:
            reagent1 = random.choice(species)
        reagent2 = random.choice(species)
        while len(reagent1.getName()) + len(reagent2.getName()) > self.getParameter("maxProductLength"):
            reagent2 = random.choice(species)
        reaction.addReactant(reagent1)
        reaction.addReactant(reagent2)
        self.addProcessedSpecies(reagent1)
        self.addProcessedSpecies(reagent2)
        productName = reagent1.getName()+reagent2.getName()
        product = [s for s in species if s.getName() == productName]
        reaction.addProduct(product[0])
        self.addProcessedSpecies(product[0])
        return reaction
    
    def checkDuplicatedReaction(self,reactions,reaction,catalyst):
        if not reactions:
            return False, None
        if catalyst.getIsCleavage():
            for r in reactions:
                if r.getCatalyst().getIsCleavage():
                    if r.getReactants()[0]==(reaction.getReactants()[0]) and r.getCatalyst().getName()==(reaction.getCatalyst().getName()) and ((r.getProducts()[0]==reaction.getProducts()[0] and r.getProducts()[1]==reaction.getProducts()[1]) or (r.getProducts()[0]==reaction.getProducts()[1] and r.getProducts()[1]==reaction.getProducts()[0])):
                        if self.debug:
                            print(greyText("PRECEDENTEMENTE TROVATA: "+r.printReaction(kauffman=True)))
                            print(colored(reaction.printReaction(kauffman=True),"red",attrs=['strike'])+" "+colored("DUPLICATA","red",attrs=['bold']))
                        return True, r
        else:
            for r in reactions:
                if r.getCatalyst().getIsCondensation():
                    if r.getReactants()[0]==(reaction.getReactants()[0]) and r.getReactants()[1]==(reaction.getReactants()[1]) and r.getCatalyst().getName()==(reaction.getCatalyst().getName()) and r.getProducts()[0]==reaction.getProducts()[0]:
                        if self.debug:
                            print(greyText("PRECEDENTEMENTE TROVATA: "+r.printReaction(kauffman=True)))
                            print(colored(reaction.printReaction(kauffman=True),"red",attrs=['strike'])+" "+colored("DUPLICATA","red",attrs=['bold']))
                        return True, r
        return False, None
        
    def generate(self, species, reactionsLimit):
        reactionsCount = 0
        duplicatedFound = False
        start = time.time()
        timeMax = float(self.getParameter('maxGenerationTime'))*60
        data = None
        autocatalysis = []
        while reactionsCount < reactionsLimit and time.time()-start < timeMax:
            catalyst = self.createCatalyst(species)
            while True:
                if catalyst.getIsCleavage():
                    reaction=self.cleave(species, catalyst)
                    if (reaction.getProducts()[0].getName() == reaction.getCatalyst().getName() or reaction.getProducts()[1].getName() == reaction.getCatalyst().getName()) and self.getParameter("autocatalysis")=="OFF":
                        autocatalysis.append(reaction)
                        continue
                else:
                    reaction=self.condense(species, catalyst)
                    if (reaction.getProducts()[0].getName() == reaction.getCatalyst().getName()) and self.getParameter("autocatalysis")=="OFF":
                        autocatalysis.append(reaction)
                        continue
                break
            self.addNotFilteredReactions(reaction)
            duplicated, r = self.checkDuplicatedReaction(self.getReactions(),reaction,catalyst)
            if not duplicated:
                self.addReaction(reaction)
            else:
                duplicatedFound = True
                if r:
                    r.setMultiplicity(r.getMultiplicity()+1)
            reactionsCount+=1
        if reactionsCount != reactionsLimit:
            data={'error':'START','lap':reactionsCount}
        return data, duplicatedFound, autocatalysis
            
    def reaction(self):
        species=self.getSpecies()
        reactionsLimit=self.getParameter("maxReactionProduced")
        if not self.debug:
            loader=Loader()
            loader.start(string="Generazione in corso")
        else:
            print(boldTitle("DUPLICAZIONI:"))
        data, duplicatedFound, autocatalysis=self.generate(species, reactionsLimit)
        self.sortSpecies()
        if not self.debug:
            loader.stop()
            pass
        else:
            if not duplicatedFound:
                print(colored("NESSUNA DUPLICAZIONE TROVATA",attrs=['bold']))
            if autocatalysis:
                print(boldTitle("AUTOCATALISI TROVATE:"))
                for r in autocatalysis:
                    print(r.printReaction(kauffman=True))
        if data:
            print(colored("TEMPO SCADUTO, GENERAZIONE INTERROTTA IN ANTICIPO","red",attrs=['bold']))
            writeReportFile(self.getParameters(),data,kauffman=True)
        else:
            deleteReportFile(kauffman=True)
        if self.debug:
            #printReactions(self.getReactions(),kauffman=True)
            print(colored("GENERAZIONE (Kauffman) TERMINATA",'red',attrs=['bold']))
        print(boldTitle("SEED UTILIZZATO: "+str(self.getSeed())))

    def output(self):
        writeOutputFile(self.getSeed(),self.getParameters(),self.getProcessedSpecies(),self.getNotFilteredReactions(),self.getReactions(),kauffman=True)
        duplicateFilesForTabulator(self.getParameters(),kauffman=True)