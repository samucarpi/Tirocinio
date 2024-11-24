from utils.parser import *
from utils.utils import *
from .objects.species import *
from .objects.catalyst import *
from .objects.reaction import *
from .objects.reactionClass import *

class Generator:
    def __init__(self, seed=None):
        self.seed = None
        self.species = []
        self.parameters = {}
        self.catalysts = []
        self.initialCondensationCatalysts = 0
        self.initialCleavageCatalysts = 0
        self.minActiveSiteLength = 0
        self.maxActiveSiteLength = 0
        self.reactionClasses = []
        self.reactions = []
    
    # Getters and setters
    def setSeed(self, seed):
        seed=generateSeed(seed)
        self.seed = seed

    def getSeed(self):
        return self.seed
    
    def setSpecies(self, species):
        self.species = species
    
    def getSpecies(self):
        return self.species
    
    def addSpecies(self, species):
        self.species.append(species)
    
    def setParameters(self, parameters):
        self.parameters = parameters

    def getParameters(self):
        return self.parameters
    
    def getParameter(self,name):
        parameters= self.getParameters()
        return parameters[name]
    
    def setCatalysts(self, catalysts):
        self.catalysts = catalysts
    
    def getCatalysts(self):
        return self.catalysts
    
    def addCatalyst(self, catalyst):
        self.catalysts.append(catalyst)

    def setInitialCondensationCatalysts(self, initialCondensationCatalysts):
        self.initialCondensationCatalysts = initialCondensationCatalysts
    
    def getInitialCondensationCatalysts(self):
        return self.initialCondensationCatalysts

    def setInitialCleavageCatalysts(self, initialCleavageCatalysts):
        self.initialCleavageCatalysts = initialCleavageCatalysts

    def getInitialCleavageCatalysts(self):
        return self.initialCleavageCatalysts
    
    def setMinActiveSiteLength(self, minActiveSiteLength):
        self.minActiveSiteLength = minActiveSiteLength

    def getMinActiveSiteLength(self):
        return self.minActiveSiteLength
    
    def setMaxActiveSiteLength(self, maxActiveSiteLength):
        self.maxActiveSiteLength = maxActiveSiteLength
    
    def getMaxActiveSiteLength(self):
        return self.maxActiveSiteLength
    
    def setReactionClasses(self, reactionClasses):
        self.reactionClasses = reactionClasses
    
    def getReactionClasses(self):
        return self.reactionClasses
    
    def addReactionClass(self, reactionClass):
        self.reactionClasses.append(reactionClass)
    
    def setReactions(self, reactions):
        self.reactions = reactions

    def getReactions(self):
        return self.reactions
    
    def addReaction(self, reaction):
        self.reactions.append(reaction)
    
    # Parameters initialization
    def initializeParameters(self):
        path=os.path.join(BASE_DIR,"IOfiles/input/parameters.txt")
        parameters = getParameters(path)
        self.setParameters(parameters)

    # Species initialization
    def initializeSpecies(self):
        path=os.path.join(BASE_DIR,"IOfiles/input/species.txt")
        species = parseInputSpecies(path)
        self.setSpecies(species)

    # Catalysts initialization
    def setInitialCatalyst(self):
        catalysts = []
        initialCondensationCatalysts = self.getInitialCondensationCatalysts()
        initialCleavageCatalysts = self.getInitialCleavageCatalysts()
        if initialCondensationCatalysts<=0 and initialCleavageCatalysts<=0:
            self.setCatalysts(catalysts)
            return
        filteredSpecies=[
            s for s in self.getSpecies()
            if((self.getParameter('maxCatalystLength') != 'ON' or len(s.name)<=self.getParameter('maxCondensationLength')) and len(s.name)>=self.getParameter('lowerLimitForCatalyst') and len(s.name)>1
            )
        ]
        catalystsNumber=initialCondensationCatalysts + initialCleavageCatalysts
        pickedSpecies=random.sample(filteredSpecies, min(catalystsNumber,len(filteredSpecies)))
        for s in pickedSpecies:
            catalyst=Catalyst(s.name, True)
            if initialCleavageCatalysts>0 and calculateProbability(self.getParameter('probabilityOfCleavage')):
                catalyst.setIsCleavage(True)
                initialCleavageCatalysts-=1
            elif initialCondensationCatalysts>0:
                catalyst.setIsCondensation(True)
                initialCondensationCatalysts-=1
            catalysts.append(catalyst)
        self.setCatalysts(catalysts)

    def initializeCatalysts(self):
        self.setInitialCondensationCatalysts(self.getParameter('initialCondensationCatalysts'))
        self.setInitialCleavageCatalysts(self.getParameter('initialCleavageCatalysts'))
        self.setInitialCatalyst()

    # Reaction class initialization
    def setActiveSiteLengthVariables(self):
        self.setMinActiveSiteLength(self.getParameter('minActiveSiteLength'))
        self.setMaxActiveSiteLength(self.getParameter('maxActiveSiteLength'))

    def setReactionClass(self,catalysts=None):
        if not catalysts:
            catalysts=self.getCatalysts()
        for c in catalysts:
            length=calculateActiveSiteLength(c,self.getMinActiveSiteLength(),self.getMaxActiveSiteLength())
            start=calculateRandomValue(0,len(c.getName())-length)
            end=start+length
            if c.getIsCondensation():
                reactionClass=CondensationReactionClass(c,start,end)
                reactionClass.condense()
            elif c.getIsCleavage():
                reactionClass=CleavageReactionClass(c,start,end)
                reactionClass.cleave()
            self.addReactionClass(reactionClass)
    
    def checkDuplicatedReactionClass(self,reactionClasses,reactionClass):
        if isinstance(reactionClass, CondensationReactionClass):
            for r in reactionClasses:
                if isinstance(r, CondensationReactionClass) and r.getReagents()[0]==reactionClass.getReagents()[0] and r.getReagents()[1]==reactionClass.getReagents()[1] and r.getCatalyst()==reactionClass.getCatalyst():
                    return True
        elif isinstance(reactionClass, CleavageReactionClass):
            for r in reactionClasses:
                if isinstance(r, CleavageReactionClass) and r.getReagents()[0]==reactionClass.getReagents()[0] and r.getCatalyst()==reactionClass.getCatalyst() and r.getSplit()==reactionClass.getSplit():
                    return True
        return False

    # Generation of new species and reactions
    def handleCondensation(self, reactionClass, species):
        print(colored(f"CLASSE DI REAZIONE R-{reactionClass.getReagents()[0]} + {reactionClass.getReagents()[1]}-R",'light_cyan',attrs=['bold']))
        reagent1Length=len(reactionClass.getReagents()[0])
        reagent2Length=len(reactionClass.getReagents()[1])
        reactions=[]
        for s in species:
            if s.getName()[-reagent1Length:]==reactionClass.getReagents()[0] and len(s.getName())<=(self.getParameter('maxCondensationLength')*2):
                reagent1=s.getName()
                for s2 in species:
                    if s2.getName()[0:reagent2Length]==reactionClass.getReagents()[1] and (len(s2.getName())+len(reagent1)) <= (self.getParameter('maxCondensationLength')*2):
                        reagent2=s2.getName()
                        result=reagent1+reagent2
                        reaction=Reaction(reactionClass)
                        reaction.setReactants([s.getName(),s2.getName(),reactionClass.getCatalyst().getName()])
                        reaction.setProducts([result,reactionClass.getCatalyst().getName()])
                        if not self.checkDuplicatedReaction(reactions,reaction,type(reactionClass)):
                            print(reagent1+" + "+reagent2+" + "+reactionClass.getCatalyst().getName()+" --> "+result+" + "+reactionClass.getCatalyst().getName())
                            reactions.append(reaction)
        return reactions

    def handleCleavage(self, reactionClass, species):
        print(colored(f"CLASSE DI REAZIONE R-{reactionClass.getReagents()[0][:reactionClass.getSplit()]} {reactionClass.getReagents()[0][reactionClass.getSplit():]}-R ",'light_cyan',attrs=['bold']))
        leftSplit=reactionClass.getReagents()[0][:reactionClass.getSplit()]
        rightSplit=reactionClass.getReagents()[0][reactionClass.getSplit():]
        leftSplitLength=len(leftSplit)
        rightSplitLength=len(rightSplit)
        reactions=[]
        for s in species:
            if self.getParameter('maxCleavageLength') == 'ON' and len(s.getName())>self.getParameter('maxCondensationLength'):
                continue
            for i in range(0,len(s.getName())-1):
                if s.getName()[i:leftSplitLength+i]==leftSplit and s.getName()[leftSplitLength+i:leftSplitLength+rightSplitLength+i]==rightSplit:
                    newSpecies1=s.getName()[0:i+reactionClass.getSplit()]
                    newSpecies2=s.getName()[i+reactionClass.getSplit():]
                    reaction=Reaction(reactionClass)
                    reaction.setReactants([s.getName(),reactionClass.getCatalyst().getName()])
                    reaction.setProducts([newSpecies1,newSpecies2,reactionClass.getCatalyst().getName()])
                    if not self.checkDuplicatedReaction(reactions,reaction,type(reactionClass)):
                        print(s.getName()+" + "+reactionClass.getCatalyst().getName()+" --> "+newSpecies1+" + "+newSpecies2+" + "+reactionClass.getCatalyst().getName())
                        reactions.append(reaction)
        return reactions
        
    def checkDuplicatedReaction(self,reactions,reaction,type):
        if not reactions:
            return False
        if type == CleavageReactionClass:
            for r in reactions:
                if r.getReactants()[0]==(reaction.getReactants()[0]) and r.getReactants()[1]==(reaction.getReactants()[1]):
                    if (r.getProducts()[0]==reaction.getProducts()[0] and r.getProducts()[1]==reaction.getProducts()[1]) or (r.getProducts()[0]==reaction.getProducts()[1] and r.getProducts()[1]==reaction.getProducts()[0]):
                        str = reaction.getReactants()[0]+" + "+reaction.getReactants()[1]+" --> "+reaction.getProducts()[0]+" + "+reaction.getProducts()[1]+" + "+reaction.getProducts()[2]
                        print(colored(str,"red",attrs=['strike'])+" "+colored("DUPLICATA","red",attrs=['bold']))
                        return True
        elif type==CondensationReactionClass:
            for r in reactions:
                if r.getReactants()[0]==(reaction.getReactants()[0]) and r.getReactants()[1]==(reaction.getReactants()[1]) and r.getReactants()[2]==(reaction.getReactants()[2]):
                    if r.getProducts()[0]==reaction.getProducts()[0]:
                        str = reaction.getReactants()[0]+" + "+reaction.getReactants()[1]+" + "+reaction.getReactants()[2]+" --> "+reaction.getProducts()[0]+" + "+reaction.getProducts()[1]
                        print(colored(str,"red",attrs=['strike'])+" "+colored("DUPLICATA","red",attrs=['bold']))
                        return True
        return False

    def generation(self,species,reactions,reactionClasses,isRecursive=False,generateOnOldSpecies=False):
        newReactions=[]
        if isRecursive:
            if generateOnOldSpecies:
                print(colored("APPLICA LE NUOVE CLASSI DI REAZIONE ALLE SPECIE VECCHIE", 'yellow', attrs=['bold']))
            else:
                print(colored("CONTINUA A GENERARE DA SPECIE PRECEDENTEMENTE GENERATE", 'yellow', attrs=['bold']))
        else:
            print(colored("GENERAZIONE DI NUOVE SPECIE", 'yellow', attrs=['bold']))
        for r in reactionClasses:
            if isinstance(r, CondensationReactionClass):
                newReactions+=self.handleCondensation(r,species)
            else:
                newReactions+=self.handleCleavage(r,species)      
        if newReactions:
            self.getReactions().extend(newReactions)
            newSpecies=[]
            oldSpecies=self.getSpecies()[:]
            for reaction in newReactions:
                self.addNewSpecies(newSpecies,reaction,type(reaction.getReactionClass()))
            if newSpecies:
                print(colored("SPECIE GENERATE",'green',attrs=['bold']))
                newReactionClasses=[]
                areNewReactionClassesGenerated=False
                for s in newSpecies:
                    if self.addRandomCataylst(s):
                        areNewReactionClassesGenerated=True
                        newReactionClasses.append(self.getReactionClasses()[-1])
                        print("• "+s.getName()+" --> SCELTA COME NUOVO CATALIZZATORE")
                        printReactionClasses([self.getReactionClasses()[-1]],new=True)
                        printReactionClasses(self.getReactionClasses())
                    else:
                        print("• "+s.getName())
                if areNewReactionClassesGenerated:
                    print(list(map(lambda s: s.getName(),oldSpecies)))
                    self.generation(oldSpecies,reactions,newReactionClasses,isRecursive=True,generateOnOldSpecies=True)
                self.generation(newSpecies,reactions,reactionClasses=self.getReactionClasses(),isRecursive=True,generateOnOldSpecies=False)
            else:
                print(colored("NESSUNA SPECIE GENERATA",'red',attrs=['bold']))
        else:
            print(colored("NESSUNA REAZIONE GENERATA",'red',attrs=['bold']))
                    
    def addNewSpecies(self,newSpecies,reaction,type):
        if type == CondensationReactionClass:
            if reaction.getProducts()[0] not in [s.getName() for s in self.getSpecies()]:
                newSpecies.append(Species(reaction.getProducts()[0], False))
                self.addSpecies(Species(reaction.getProducts()[0], False))
        elif type == CleavageReactionClass:
            if reaction.getProducts()[0] not in [s.getName() for s in self.getSpecies()]:
                newSpecies.append(Species(reaction.getProducts()[0], False))
                self.addSpecies(Species(reaction.getProducts()[0], False))
            if reaction.getProducts()[1] not in [s.getName() for s in self.getSpecies()]:
                newSpecies.append(Species(reaction.getProducts()[1], False))
                self.addSpecies(Species(reaction.getProducts()[1], False))
                
    
    def addRandomCataylst(self,species):
        if self.getParameter('maxCatalystLength')=='ON' and len(species.name)>self.getParameter('maxCondensationLength'):
            return
        if len(species.name)>=self.getParameter('lowerLimitForCatalyst') and len(species.name)>1:
            isCatalyst=calculateProbability(self.getParameter('probabilityOfCatalyst'))
            if isCatalyst:
                catalyst=Catalyst(species.name, False)
                if calculateProbability(self.getParameter('probabilityOfCleavage')):   
                    catalyst.setIsCleavage(True)
                else:
                    catalyst.setIsCondensation(True)
                self.addCatalyst(catalyst)
                self.setReactionClass([catalyst])
                return True
        return False
    
    # Initialization and reaction main functions
    def initialization(self):
        self.initializeParameters()
        self.setSeed(self.getParameter('seed'))
        printParameters(self.getParameters())
        self.initializeSpecies()
        printSpecies(self.getSpecies())
        self.initializeCatalysts()

    def reaction(self):
        self.setActiveSiteLengthVariables()
        self.setReactionClass()
        printReactionClasses(self.getReactionClasses())
        species=self.getSpecies()
        reactionClasses=self.getReactionClasses()
        reactions=[]
        self.generation(species,reactions,reactionClasses,isRecursive=False,generateOnOldSpecies=False)
        print(colored("GENERAZIONE TERMINATA",'red',attrs=['bold']))
        printReactions(self.getReactions())
        printSpecies(self.getSpecies(),ended=True)

    def output(self):
        writeOutputFile(self.getParameters(),self.getSpecies(),self.getReactions())

            