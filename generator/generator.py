from utils.parser import *
from utils.utils import *
from utils.loader import *
from generator.objects.species import *
from generator.objects.catalyst import *
from generator.objects.reaction import *
from generator.objects.reactionClass import *
from collections import deque
import time

class Generator:
    def __init__(self, debug):
        self.debug = debug
        self.seed = None
        self.parameters = {}
        self.species = []
        self.catalysts = []
        self.initialCondensationCatalysts = 0
        self.initialCleavageCatalysts = 0
        self.minActiveSiteLength = 0
        self.maxActiveSiteLength = 0
        self.reactionClasses = []
        self.reactions = []
        self.notFilteredReactions = []
    
    # Getters and setters
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
    
    def addSpecies(self, species):
        self.species.append(species)
    
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

    def setNotFilteredReactions(self, notFilteredReactions):
        self.notFilteredReactions = notFilteredReactions
    
    def getNotFilteredReactions(self):
        return self.notFilteredReactions
    
    def addNotFilteredReactions(self, notFilteredReactions):
        self.notFilteredReactions.append(notFilteredReactions)
    
    # Parameters initialization
    def initializeParameters(self,mutator=False):
        if mutator:
            error,parameters = getParameters(MUTATOR_PARAMETERS_FILE, self.getSpecies())
        else:
            error,parameters = getParameters(GENERATOR_PARAMETERS_FILE, self.getSpecies())
        if error:
            for message in parameters:
                print(colored(message,"red",attrs=['bold']))
            exit()
        else:
            self.setParameters(parameters)

    # Species initialization
    def initializeSpecies(self):
        species = parseInputSpecies(GENERATOR_SPECIES_FILE)
        for s in species:
            s.setIsInitial(True)
        self.setSpecies(species)

    def setFood(self): 
        food = getFileData(GENERATOR_FOOD_FILE)
        check = True
        if food:
            species = [s.getName() for s in self.getSpecies()]
            for f in food:
                if f not in species:
                    check = False
                    break
        else:
            print(colored("ATTENZIONE! PER AVVIARE LA GENERAZIONE È NECESSARIO SPECIFICARE ALMENO UNA SPECIE FOOD","red",attrs=['bold']))
            exit()
        if not check:
            print(colored("ATTENZIONE! IL CIBO NON È UN SOTTOINSIEME DELLE SPECIE PRESENTI","red",attrs=['bold']))
            exit()
        for s in self.getSpecies():
            if s.getName() in food:
                s.setIsFood(True)

    # Catalysts initialization
    def setInitialCatalyst(self):
        catalysts = []
        initialCondensationCatalysts = self.getInitialCondensationCatalysts()
        initialCleavageCatalysts = self.getInitialCleavageCatalysts()
        if initialCondensationCatalysts<=0 and initialCleavageCatalysts<=0:
            self.setCatalysts(catalysts)
            return
        filteredSpecies=[
            s for s in self.getSpecies() if((self.getParameter('maxCatalystLength') != 'ON' or len(s.getName())<=self.getParameter('maxCondensationLength')) and len(s.getName())>=self.getParameter('lowerLimitForCatalyst') and len(s.getName())>1 and s.getName() and not s.getIsFood())
        ]
        catalystsNumber=initialCondensationCatalysts + initialCleavageCatalysts
        pickedSpecies=random.sample(filteredSpecies, min(catalystsNumber,len(filteredSpecies)))
        for s in pickedSpecies:
            catalyst=Catalyst(s.getName())
            catalyst.setIsInitial(True)
            if initialCleavageCatalysts>0 and (initialCondensationCatalysts<=0 or not calculateProbability(self.getParameter('probabilityOfCleavage'))):
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
            while True:
                length=calculateActiveSiteLength(c,self.getMinActiveSiteLength(),self.getMaxActiveSiteLength())
                start=calculateRandomValue(0,len(c.getName())-length)
                end=start+length
                if c.getIsCondensation():
                    reactionClass=CondensationReactionClass(c,start,end)
                    reactionClass.condense(self.getParameter('monomers'))
                elif c.getIsCleavage():
                    reactionClass=CleavageReactionClass(c,start,end)
                    reactionClass.cleave(self.getParameter('monomers'))
                if not self.checkDuplicatedReactionClass(self.getReactionClasses(),reactionClass):
                    self.addReactionClass(reactionClass)
                    break
                else:
                    if self.debug:
                        printReactionClasses(self.getReactionClasses())
                        printReactionClasses([reactionClass],new=True)
                        print(colored("REGOLA DUPLICATA, RIGENERO","red",attrs=['bold']))

    def checkDuplicatedReactionClass(self,reactionClasses,reactionClass):
        if not reactionClasses:
            return False
        if isinstance(reactionClass, CondensationReactionClass):
            for r in reactionClasses:
                if isinstance(r,CondensationReactionClass) and r.getReagents()[0]==reactionClass.getReagents()[0] and r.getReagents()[1]==reactionClass.getReagents()[1] and r.getCatalyst().getName()==reactionClass.getCatalyst().getName():
                    return True
        elif isinstance(reactionClass, CleavageReactionClass):
            for r in reactionClasses:
                if isinstance(r,CleavageReactionClass) and r.getReagents()[0]==reactionClass.getReagents()[0] and r.getCatalyst().getName()==reactionClass.getCatalyst().getName() and r.getSplit()==reactionClass.getSplit():
                    return True
        return False

    # Generation of new species and reactions
    def handleCondensation(self,reactionClass,species):
        if self.debug:
            print(colored(f"CLASSE DI REAZIONE R-{reactionClass.getReagents()[0]} + {reactionClass.getReagents()[1]}-R",'light_cyan',attrs=['bold']))
        reagent1Length=len(reactionClass.getReagents()[0])
        reagent2Length=len(reactionClass.getReagents()[1])
        reactions,notFilteredReactions=[],[]
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
                        notFilteredReactions.append(reaction)
                        [duplicatedLocal,rLocal]=self.checkDuplicatedReaction(reactions,reaction,type(reactionClass))
                        [duplicatedGlobal,rGlobal]=self.checkDuplicatedReaction(self.getReactions(),reaction,type(reactionClass))
                        if not duplicatedLocal and not duplicatedGlobal:
                            if self.debug:
                                print(reaction.printReaction())
                            reactions.append(reaction)
                        else:
                            if rLocal:
                                rLocal.setMultiplicity(rLocal.getMultiplicity()+1)
                            if rGlobal:
                                rGlobal.setMultiplicity(rGlobal.getMultiplicity()+1)
        self.getNotFilteredReactions().extend(notFilteredReactions)
        return reactions

    def handleCleavage(self, reactionClass, species):
        if self.debug:
            print(colored(f"CLASSE DI REAZIONE R-{reactionClass.getReagents()[0][:reactionClass.getSplit()]} {reactionClass.getReagents()[0][reactionClass.getSplit():]}-R ",'light_cyan',attrs=['bold']))
        leftSplit=reactionClass.getReagents()[0][:reactionClass.getSplit()]
        rightSplit=reactionClass.getReagents()[0][reactionClass.getSplit():]
        leftSplitLength=len(leftSplit)
        rightSplitLength=len(rightSplit)
        reactions,notFilteredReactions=[],[]
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
                    notFilteredReactions.append(reaction)
                    [duplicatedLocal,rLocal]=self.checkDuplicatedReaction(reactions,reaction,type(reactionClass))
                    [duplicatedGlobal,rGlobal]=self.checkDuplicatedReaction(self.getReactions(),reaction,type(reactionClass))
                    if not duplicatedLocal and not duplicatedGlobal:
                        if self.debug:
                            print(reaction.printReaction())
                        reactions.append(reaction)
                    else:
                        if rLocal:
                            rLocal.setMultiplicity(rLocal.getMultiplicity()+1)
                        if rGlobal:
                            rGlobal.setMultiplicity(rGlobal.getMultiplicity()+1)
        self.getNotFilteredReactions().extend(notFilteredReactions)
        return reactions

    def checkDuplicatedReaction(self,reactions,reaction,type):
        if not reactions:
            return False, None
        if type == CleavageReactionClass:
            for r in reactions:
                if isinstance(r.getReactionClass(),CleavageReactionClass) and r.getReactants()[0]==(reaction.getReactants()[0]) and r.getReactants()[1]==(reaction.getReactants()[1]) and ((r.getProducts()[0]==reaction.getProducts()[0] and r.getProducts()[1]==reaction.getProducts()[1]) or (r.getProducts()[0]==reaction.getProducts()[1] and r.getProducts()[1]==reaction.getProducts()[0])):
                    if self.debug:
                        print(colored(reaction.printReaction(),"red",attrs=['strike'])+" "+colored("DUPLICATA","red",attrs=['bold']))
                    return True, r
        elif type == CondensationReactionClass:
            for r in reactions:
                if isinstance(r.getReactionClass(),CondensationReactionClass) and r.getReactants()[0]==(reaction.getReactants()[0]) and r.getReactants()[1]==(reaction.getReactants()[1]) and r.getReactants()[2]==(reaction.getReactants()[2]) and r.getProducts()[0]==reaction.getProducts()[0]:
                    if self.debug:
                        print(colored(reaction.printReaction(),"red",attrs=['strike'])+" "+colored("DUPLICATA","red",attrs=['bold']))
                    return True, r
        return False, None

    def generation(self, species, reactions, reactionClasses, isRecursive=False, generateOnOldSpecies=False,mutator=False):
        queue = deque([(species,reactions,reactionClasses,isRecursive,generateOnOldSpecies,mutator)])
        processedSpecies = set()
        timeMax = float(self.getParameter('maxGenerationTime'))*60
        start = time.time()
        lap=0
        while queue:
            if(time.time()-start)>=timeMax:
                data={'error':'START','lap':lap}
                return data
            #get the first element of the queue
            currentSpecies,currentReactions,currentReactionClasses,currentIsRecursive,currentGenerateOnOldSpecies,mutator = queue.popleft()
            #if the generation is for new species, remove the species already processed
            if not currentGenerateOnOldSpecies:
                currentSpecies = [s for s in currentSpecies if s.getName() not in processedSpecies]
            #update the set of processed species
            processedSpecies.update(s.getName() for s in currentSpecies)
            if self.debug:
                if currentIsRecursive:
                    if currentGenerateOnOldSpecies:
                        print(colored("APPLICA LE NUOVE CLASSI DI REAZIONE ALLE SPECIE VECCHIE "+str(list(map(lambda s: s.getName(),currentSpecies))),'yellow',attrs=['bold']))
                    else:
                        if mutator:
                            print(colored("CONTINUA A GENERARE DALLE SPECIE INTRODOTTE "+str(list(map(lambda s: s.getName(),currentSpecies))),'yellow',attrs=['bold']))
                            mutator = False
                        else:
                            print(colored("CONTINUA A GENERARE DA SPECIE PRECEDENTEMENTE GENERATE "+str(list(map(lambda s: s.getName(),currentSpecies))),'yellow',attrs=['bold']))
                else:
                    print(colored("GENERAZIONE DI NUOVE SPECIE",'yellow',attrs=['bold']))
            #for each species, apply the reaction classes
            newReactions = []
            processedReactionClasses = []
            for r in currentReactionClasses:
                if(time.time()-start)>=timeMax:
                    data={'error':'REACTION','lap':lap,'reactionClasses':currentReactionClasses,'processedReactionClasses':processedReactionClasses}
                    return data
                if isinstance(r,CondensationReactionClass):
                    reactions=self.handleCondensation(r,currentSpecies)
                    newReactions+=reactions
                else:
                    reactions=self.handleCleavage(r,currentSpecies)
                    newReactions+=reactions
                processedReactionClasses.append(r)
            if newReactions:
                #if new reactions are generated, add the new reactions to the list of reactions
                self.getReactions().extend(newReactions)
                newSpecies = []
                oldSpecies = self.getSpecies()[:]
                #for each new reaction, add the new species generated
                processedReactions=[]
                for reaction in newReactions:
                    if(time.time()-start)>=timeMax:
                        data={'error':'SPECIES','lap':lap,'reactions':newReactions,'processedReactions':processedReactions}
                        return data
                    self.addNewSpecies(newSpecies,reaction,type(reaction.getReactionClass()))
                    processedReactions.append(reaction)
                if newSpecies:
                    if self.debug:
                        print(colored("SPECIE GENERATE",'green',attrs=['bold']))
                    newReactionClasses = []
                    areNewReactionClassesGenerated=False
                    #for each new species, add a random catalyst
                    for s in newSpecies:
                        if self.addRandomCataylst(s):
                            areNewReactionClassesGenerated=True
                            newReactionClasses.append(self.getReactionClasses()[-1])
                            if self.debug:
                                print("• "+s.getName()+" --> SCELTA COME NUOVO CATALIZZATORE")
                                printReactionClasses([self.getReactionClasses()[-1]],new=True)
                                printReactionClasses(self.getReactionClasses())
                        else:
                            if self.debug:
                                print("• "+s.getName())
                    # if new reaction classes are generated, add the new reaction classes to the list of reaction classes and generate new reactions
                    # first with the old species and then with the new species
                    if areNewReactionClassesGenerated:
                        queue.append((oldSpecies,currentReactions,newReactionClasses,True,True,mutator))
                    queue.append((newSpecies,currentReactions,self.getReactionClasses(),True,False,mutator))
                else:
                    if self.debug:
                        print(colored("NESSUNA SPECIE GENERATA",'red',attrs=['bold']))
            else:
                if self.debug:
                    print(colored("NESSUNA REAZIONE GENERATA",'red',attrs=['bold']))
            lap+=1
                    
    def addNewSpecies(self,newSpecies,reaction,type):
        species=None
        if type == CondensationReactionClass:
            if reaction.getProducts()[0] not in [s.getName() for s in self.getSpecies()]:
                species = createSpeciesObject(reaction.getProducts()[0])
        elif type == CleavageReactionClass:
            if reaction.getProducts()[0] not in [s.getName() for s in self.getSpecies()]:
                species = createSpeciesObject(reaction.getProducts()[0])
            if reaction.getProducts()[1] not in [s.getName() for s in self.getSpecies()]:
                species = createSpeciesObject(reaction.getProducts()[1])
        if species:
            species.setIsInitial(False)
            newSpecies.append(species)
            self.addSpecies(species)
                
    def addRandomCataylst(self,species):
        if self.getParameter('maxCatalystLength')=='ON' and len(species.getName())>self.getParameter('maxCondensationLength'):
            return
        if len(species.getName())>=self.getParameter('lowerLimitForCatalyst') and len(species.getName())>1 and not species.getIsFood():
            isCatalyst=calculateProbability(self.getParameter('probabilityOfCatalyst'))
            if isCatalyst:
                catalyst=Catalyst(species.getName())
                catalyst.setIsInitial(False)
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
        self.initializeSpecies()
        self.initializeParameters()
        self.setSeed(self.getParameter('seed'))
        self.setFood()
        if self.debug:
            printParameters(self.getParameters())
            printSpecies(self.getSpecies())
        self.initializeCatalysts()
        
    def reaction(self):
        self.setActiveSiteLengthVariables()
        self.setReactionClass()
        if self.debug:
            printReactionClasses(self.getReactionClasses())
        species=self.getSpecies()
        reactionClasses=self.getReactionClasses()
        if not self.debug:
            loader=Loader()
            loader.start(string="Generazione in corso")
        reactions=[]
        data=self.generation(species,reactions,reactionClasses,isRecursive=False,generateOnOldSpecies=False)
        if not self.debug:
            loader.stop()
        if data:
            if self.debug:
                print(colored("TEMPO SCADUTO, GENERAZIONE INTERROTTA IN ANTICIPO","red",attrs=['bold']))
            writeReportFile(self.getParameters(),data)
        else:
            deleteReportFile()
        if self.debug:
            printReactions(self.getReactions())
            printSpecies(self.getSpecies(),ended=True)
            print(colored("GENERAZIONE (con complementarietà) TERMINATA",'red',attrs=['bold']))
        print(boldTitle("SEED UTILIZZATO: "+str(self.getSeed())))

    def output(self,mutator=False):
        writeOutputFile(self.getSeed(),self.getParameters(),self.getSpecies(),self.getNotFilteredReactions(),self.getReactions(),mutator=mutator)
        writeRulesFile(self.getParameters(),self.getReactionClasses(),mutator=mutator)
        duplicateFilesForTabulator(self.getParameters(),mutator=mutator)