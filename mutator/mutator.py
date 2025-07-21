from generator.generator import Generator, Species, Catalyst, Reaction, CleavageReactionClass, CondensationReactionClass
from utils.utils import *
from utils.parser import createSpeciesObject, getFileData
from utils.loader import Loader
import difflib

class Mutator():
    def __init__(self, debug):
        self.debug = debug
        self.species = []
        self.reactionClasses = []
        self.reactions = []
        self.newSpecies = []
        self.newReactionClasses = []
        self.generator = None

    def getDebug(self):
        return self.debug

    def setGenerator(self, generator):
        self.generator = generator

    def getGenerator(self):
        return self.generator

    def addSpecies(self, species):
        self.species.append(species)

    def setSpecies(self,lines):
        for line in lines:
            if line.startswith("Cont"):
                line = lines[lines.index(line) + 1]
                while not line.startswith("10.0"):
                    name = line.split()[0]
                    self.addSpecies(createSpeciesObject(name))
                    line = lines[lines.index(line) + 1]
    
    def getSpecies(self):
        return self.species
    
    def setFood(self,lines):
        for line in lines:
            if line.startswith("10.0"):
                name = line.split()[2]
                for species in self.species:
                    if species.getName() == name:
                        species.setIsFood(True)

    def addReactionClass(self, reactionClass):
        self.reactionClasses.append(reactionClass)                    
    
    def setReactionClasses(self, lines):
        lines = lines[1:]
        for line in lines:
            line = line.split()
            if line[1] == "Cleavage":
                for species in self.getSpecies():
                    if species.getName() == line[0]:
                        catalyst = Catalyst(species.getName())
                        catalyst.setIsCleavage(True)
                        break
                reagent1 = line[4].replace("R-", "")
                reagent2 = line[5].replace("-R", "")
                reagent = reagent1 + reagent2
                start = catalyst.getName().find(line[2])
                end = start + len(line[2])
                reactionClass = CleavageReactionClass(
                    catalyst = catalyst,
                    start = start,
                    end = end
                )
                reactionClass.setReagents([reagent])
                reactionClass.setSplit(int(line[3]))
            elif line[1] == "Condensazione":
                for species in self.getSpecies():
                    if species.getName() == line[0]:
                        catalyst = Catalyst(species.getName())
                        catalyst.setIsCondensation(True)
                        break
                reagents = line[4].split("+")
                reagent1 = reagents[0].replace("R-", "")
                reagent2 = reagents[1].replace("-R", "")
                start = catalyst.getName().find(line[2])
                end = start + len(line[2])
                reactionClass = CondensationReactionClass(
                    catalyst = catalyst,
                    start = start,
                    end = end
                )
                reactionClass.setReagents([reagent1, reagent2])
                reactionClass.setSplit(int(line[3]))
            self.addReactionClass(reactionClass)
    
    def getReactionClasses(self):
        return self.reactionClasses
    
    def addReaction(self, reaction):
        self.reactions.append(reaction)

    def setReaction(self, line):
        check = line.split(">")
        reactants = check[0].split("+")
        reactants = [reactant.strip() for reactant in reactants]
        products = check[1].split("+")
        products = [product.strip() for product in products]
        if len(reactants) == 3:
            catalyst = reactants[2]
            products = [products[0],catalyst]
        elif len(reactants) == 2:
            catalyst = reactants[1]
            products = [products[0],products[1],catalyst]
        for reactionClass in self.getReactionClasses():
            if reactionClass.getCatalyst().getName() == catalyst:
                reaction = Reaction(reactionClass)
                reaction.setReactants(reactants)
                reaction.setProducts(products)
                reaction.setCatalyst(reactionClass.getCatalyst())
                self.addReaction(reaction)

    def setReactions(self, lines):
        trigger=False
        flag=False
        for line in lines:
            if not trigger:
                if line.startswith("10.0"):
                    trigger=True
                continue
            else:
                if not flag:
                    if not line.startswith("10.0"):
                        flag = True
                        if "NESSUNA REAZIONE GENERATA" in line:
                            continue
                        else:
                            self.setReaction(line)
                else:
                    self.setReaction(line)

    def getReactions(self):
        return self.reactions
    
    def initializeGenerator(self):
        g = Generator(self.getDebug())
        g.setSpecies(self.getSpecies())
        g.initializeParameters(mutator=True)
        g.setSeed(g.getParameter('seed'))
        g.setReactionClasses(self.getReactionClasses())
        g.setReactions(self.getReactions())
        g.setMinActiveSiteLength(g.getParameter('minActiveSiteLength'))
        g.setMaxActiveSiteLength(g.getParameter('maxActiveSiteLength'))
        self.setGenerator(g)
    
    def getNewSpecies(self):
        return self.newSpecies
    
    def addNewSpecies(self, species):
        self.newSpecies.append(species)

    def getNewReactionClasses(self):
        return self.newReactionClasses
    
    def addNewReactionClass(self, reactionClass):
        self.newReactionClasses.append(reactionClass)

    def setNewSpecies(self, lines, g):
        newReactionClass = False
        lines = lines[1:]
        for line in lines:
            line = line.split()
            name = line[0]
            if name in [s.getName() for s in g.getSpecies()]:
                print(colored("ATTENZIONE! La specie "+name+" è già presente nella lista delle specie.","red",attrs=['bold']))
                exit()
            match(line[1]):
                case "B":
                    species = Species(name)
                    self.addNewSpecies(species)
                case "C":
                    if g.getParameter('maxCatalystLength')=='ON' and len(name)>g.getParameter('maxCondensationLength'):
                        print(colored("ATTENZIONE! La specie catalizzatore "+name+" non può essere più lunga di \"MASSIMA LUNGHEZZA PER CONDENSAZIONI\".","red",attrs=['bold']))
                        exit()
                    if len(name)<g.getParameter('lowerLimitForCatalyst'):
                        print(colored("ATTENZIONE! La specie catalizzatore "+name+" non può essere più corta di \"LIMITE INFERIORE PER ESSERE CATALIZZATORE\".","red",attrs=['bold']))
                        exit()
                    if len(name)<=1:
                        print(colored("ATTENZIONE! La specie catalizzatore "+name+" non può essere lunga 1 carattere.","red",attrs=['bold']))
                        exit()
                    catalyst = Catalyst(name)
                    self.addNewSpecies(catalyst)
                    if calculateProbability(g.getParameter('probabilityOfCleavage')):   
                        catalyst.setIsCleavage(True)
                    else:
                        catalyst.setIsCondensation(True)
                    while True:
                        length=calculateActiveSiteLength(catalyst,g.getMinActiveSiteLength(),g.getMaxActiveSiteLength())
                        start=calculateRandomValue(0,len(catalyst.getName())-length)
                        end=start+length
                        if catalyst.getIsCondensation():
                            reactionClass=CondensationReactionClass(catalyst,start,end)
                            reactionClass.condense(g.getParameter('monomers'))
                        elif catalyst.getIsCleavage():
                            reactionClass=CleavageReactionClass(catalyst,start,end)
                            reactionClass.cleave(g.getParameter('monomers'))
                        if not g.checkDuplicatedReactionClass(g.getReactionClasses(),reactionClass):
                            self.addNewReactionClass(reactionClass)
                            break
                    newReactionClass = True
                case "F":
                    species = Species(name)
                    species.setIsFood(True)
                    self.addNewSpecies(species)
        return newReactionClass

    def initialization(self):
        chemistry = readFile(MUTATOR_CHEMISTRY_FILE)
        chemistry = [line.strip() for line in chemistry if line.strip()]
        self.setSpecies(chemistry)
        self.setFood(chemistry)
        rules = readFile(MUTATOR_RULES_FILE)
        rules = [line.strip() for line in rules if line.strip()]
        self.setReactionClasses(rules)
        self.setReactions(chemistry)
        self.initializeGenerator()

    def mutate(self):
        g = self.getGenerator()
        newSpecies = getFileData(MUTATOR_SPECIES_FILE)
        newReactionClass = self.setNewSpecies(newSpecies,g)
        if newReactionClass:
            if self.getNewReactionClasses():
                for rc in self.getNewReactionClasses():
                    g.addReactionClass(rc)
                if self.getDebug():
                    printReactionClasses([rc],new=True)
            data = g.generation(g.getSpecies(), g.getReactions(), self.getNewReactionClasses(),isRecursive=True,generateOnOldSpecies=True)
            if not data:
                deleteReportFile(mutator=True)
                for s in self.getNewSpecies():
                    g.addSpecies(s)
                data = g.generation(self.getNewSpecies(), g.getReactions(), g.getReactionClasses(),isRecursive=True,generateOnOldSpecies=False,mutator=True)
            if data:
                if self.debug:
                    print(colored("TEMPO SCADUTO, GENERAZIONE INTERROTTA IN ANTICIPO","red",attrs=['bold']))
                writeReportFile(g.getParameters(),data)
            else:
                deleteReportFile(mutator=True)
        if self.debug:
            printReactions(g.getReactions())
            printSpecies(g.getSpecies(),ended=True)
        print(boldTitle("SEED UTILIZZATO: "+str(g.getSeed())))

    def writeOutputFiles(self):
        g = self.getGenerator()
        g.output(mutator=True)
        with open(MUTATOR_CHEMISTRY_FILE) as chemistryFile, open(MUTATOR_OUTPUT_FILE) as outputFile:
            lines1 = chemistryFile.readlines()
            lines2 = outputFile.readlines()
        diff = difflib.ndiff(lines1, lines2)
        with open(MUTATOR_DIFFERENCE_FILE, 'w') as diffFile:
            for line in diff:
                diffFile.write(line)
