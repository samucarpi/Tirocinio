from utils.utils import *
from utils.parser import parseInputSpecies, getEvolverParameters, getParameters
from launcher.launcher import runVenturi, formatFileForVenturi
from utils.loader import Loader

class Evolver:
    def __init__(self, debug):
        self.debug = debug
        self.parameters = {}
        self.chemistryParameters = {}
        self.previousTime = 600000
        self.concentrations = {}
        self.containerCatalysts = []
        self.currentIntroducedSpecies = []

    def getDebug(self):
        return self.debug
    
    def setParameters(self, parameters):
        error, parameters = getEvolverParameters(parameters)
        if error:
            for message in parameters:
                print(colored(message, "red", attrs=['bold']))
            exit(0)
        else:
            self.parameters = parameters

    def getParameters(self):
        return self.parameters
    
    def getParameter(self, name):
        parameters = self.getParameters()
        return parameters[name]
    
    def getChemistryParameters(self):
        return self.chemistryParameters
    
    def setChemistryParameters(self):
        species = parseInputSpecies(GENERATOR_SPECIES_FILE)
        error, parameters = getParameters(GENERATOR_PARAMETERS_FILE, species)
        if error:
            for message in parameters:
                print(colored(message, "red", attrs=['bold']))
            exit(0)
        else:
            self.chemistryParameters = parameters
    
    def getChemistryParameter(self, name):
        chemistryParameters = self.getChemistryParameters()
        return chemistryParameters[name]

    def getPreviousTime(self):
        return self.previousTime

    def setPreviousTime(self, time):
        self.previousTime = time

    def getConcentrations(self):
        return self.concentrations
    
    def setConcentrations(self, concentrations):
        self.concentrations = concentrations

    def getSingleConcentration(self, species):
        concentrations = self.getConcentrations()
        return concentrations.get(species, "0.0")
    
    def setContainerCatalysts(self, catalysts):
        self.containerCatalysts = catalysts

    def getContainerCatalysts(self):
        return self.containerCatalysts

    def getCurrentIntroducedSpecies(self):
        return self.currentIntroducedSpecies

    def setCurrentIntroducedSpecies(self, species):
        self.currentIntroducedSpecies = species
    
    def addCurrentIntroducedSpecies(self, species):
        self.currentIntroducedSpecies.append(species)

    def clearCurrentIntroducedSpecies(self):
        self.currentIntroducedSpecies.clear()

    def copyChemistryFiles(self):
        copyFile(GENERATOR_PARAMETERS_FILE, EVOLVER_CHEMISTRY_PARAMETERS_FILE)
        self.setChemistryParameters()
        chemistryName = self.getChemistryParameter("outputFile")+"-uniqueReactions.txt"
        chemistryFile = os.path.join(BASE_DIR,"io","generator","output",chemistryName)
        rulesName = self.getChemistryParameter("outputRulesFile")
        rulesFile = os.path.join(BASE_DIR,"io","generator","output",rulesName)
        copyFile(chemistryFile, EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE)
        copyFile(rulesFile, EVOLVER_CHEMISTRY_RULES_FILE)

    def checkRAF(self, file):
        if "In" not in os.listdir(VENTURI):
            os.makedirs(os.path.join(VENTURI, "In"))
        if "Out" not in os.listdir(VENTURI):
            os.makedirs(os.path.join(VENTURI, "Out"))
        venturiInputPath = os.path.join(VENTURI, "In","chemistry.txt")
        copyFile(file, venturiInputPath)
        formatFileForVenturi(venturiInputPath)
        if self.getDebug():
            loader=Loader()
            loader.start("Ricerca di RAF in corso")
        runVenturi(VENTURI)
        if self.getDebug():
            loader.stop()
        venturiOutputPath = os.path.join(VENTURI, "Out")
        if os.listdir(venturiOutputPath):
            if self.getDebug():
                print(colored("RAF individuato","green",attrs=['underline']))
            shutil.rmtree(venturiOutputPath)
            os.makedirs(venturiOutputPath)
            return True
        else:
            if self.getDebug():
                print(colored("RAF non individuato","red",attrs=['underline']))
            return False
        
    def pickContainerCatalysts(self):
        species = getSpeciesNamesFromFile(EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE)
        food = getFoodsNamesFromFile(EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE)
        filteredSpecies = [s for s in species if s not in food or s.startswith("Cont")]
        pickedSpecies=random.sample(filteredSpecies, self.getParameter("numberOfMembraneCatalysts"))
        return pickedSpecies
    
    def writeContainerSpeciesFile(self, initialize=False):
        concExtFC = "10"
        mdiffFC = "1.00e-18"
        alfa = "1.00e-02"
        i = 0
        max_length = max(len(c) for c in self.getContainerCatalysts())
        with open(PITZALIS_CONTAINERS_RULES, "w") as f:
            f.write(f"{"NomeFC":<12} {"QFC":<12} {"ConcExtFC":<13} {"MdiffFC":<11} {"NomeCatFC":<{max_length+5}} {"Alfa":<10}\n")
            for c in self.getContainerCatalysts():
                if not initialize:
                    qfc = self.getSingleConcentration("FC"+str(i))
                else:
                    qfc = "1.00e-18"
                f.write(f"FC{i:<10} {qfc:<12} {concExtFC:<13} {mdiffFC:<11} {c:<{max_length+5}} {alfa:<10}\n")
                i+=1
        
    def addContainerSpecies(self,firstLap=False):
        self.writeContainerSpeciesFile(initialize=firstLap)
        copyFile(EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE, PITZALIS_CONTAINERS_SPECIES_INPUT)
        runPitzalisContainers(PITZALIS)
        formatFile(PITZALIS_CONTAINERS_SPECIES_OUTPUT)
        copyFile(PITZALIS_CONTAINERS_SPECIES_OUTPUT, EVOLVER_CHEMISTRY_WITH_CONTAINER_FILE)

    def pitzalisSimulator(self):
        copyFile(EVOLVER_CHEMISTRY_WITH_CONTAINER_FILE, PITZALIS_INPUT)
        runPitzalisSimulator(PITZALIS)
        shutil.rmtree(EVOLVER_OUTPUT)
        os.makedirs(EVOLVER_OUTPUT, exist_ok=True)
        shutil.copytree(PITZALIS_OUTPUT, EVOLVER_OUTPUT, dirs_exist_ok=True)
        time = float(readFile(PITZALIS_TIME)[0].strip())
        self.setConcentrations(getSpeciesConcentrations(PITZALIS_QUANTITIES))
        return time

    def writeMutatorSpeciesFile(self, speciesFile):
        self.clearCurrentIntroducedSpecies()
        species = getSpeciesNamesFromFile(EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE)
        max_length = max(len(s) for s in species)
        monomers = [m["name"] for m in self.getChemistryParameter("monomers")]
        allCombinations = monomerCombinations(monomers, max_length)
        probabilityOfTypes = self.getParameter("probabilityOfTypes")
        pickedType = random.choices(list(probabilityOfTypes.keys()), list(probabilityOfTypes.values()), k=1)[0]
        if pickedType == "B":
            filteredCombinations = [s for s in allCombinations if not (s.startswith("Cont") or s in species)]
            pickedSpecies=random.sample(filteredCombinations, self.getParameter("numberOfIntroducedSpecies"))
            for s in pickedSpecies:
                self.addCurrentIntroducedSpecies({"name": s, "type": "B"})
        elif pickedType == "C":
            filteredCombinations = []
            for s in allCombinations:
                if s.startswith("Cont") or s in species:
                    continue
                if self.getChemistryParameter('maxCatalystLength')=='ON' and len(s)>self.getChemistryParameter('maxCondensationLength'):
                    continue
                if len(s)<self.getChemistryParameter('lowerLimitForCatalyst'):
                    continue
                if len(s)<=1:
                    continue
                filteredCombinations.append(s)
            pickedSpecies=random.sample(filteredCombinations, 1)
            self.setCurrentIntroducedSpecies([{"name": pickedSpecies[0], "type": "C"}])
        elif pickedType == "F":
            catalysts = getCatalystsNamesFromFile(EVOLVER_CHEMISTRY_RULES_FILE)
            filteredCombinations = [s for s in species if (not s.startswith("Cont") and s not in catalysts)]
            pickedSpecies=random.sample(filteredCombinations, 1)
            self.setCurrentIntroducedSpecies([{"name": pickedSpecies[0], "type": "F"}])
        maxLengthIntroduced = max(len(s) for s in pickedSpecies)+5
        with open(speciesFile, "w") as f:
            string = f"# FILE DI INSERIMENTO DELLE SPECIE CHIMICHE MUTANTI\n\n# FORMATTAZIONE\n# NOME TIPO\n# IL TIPO PUO' ESSERE DI TIPO: FOOD (F), CATALIZZATORE (C), BASE (B)\n"
            f.writelines(string+"\n")
            f.write(f"{'SPECIE':<{maxLengthIntroduced}}{'TIPO':<{5}}\n")
            type=self.getCurrentIntroducedSpecies()[0]['type']
            for s in pickedSpecies:
                f.write(f"{s:<{maxLengthIntroduced}}{type:<{5}}\n")

    def updateConcentrationsMutatedChemistry(self, mutatedChemistryFile):
        introducedSpecies = [d['name'] for d in self.getCurrentIntroducedSpecies()]
        with open(mutatedChemistryFile, "r") as f:
            lines = f.readlines()
        with open(mutatedChemistryFile, "w") as f:
            for line in lines:
                if not NUMERIC_START.match(line) and not "+" in line and line.strip() and not line.startswith("#") and not line.startswith("SEED"):
                    line = line.split()
                    if line[0] in introducedSpecies:
                        line[1] = str(self.getParameter("concentrationIntroducedSpecies"))
                    else:
                        line[1] = str(self.getSingleConcentration(line[0]))
                    f.write(" ".join(line) + "\n")
                else:
                    f.write(line)

    def mutateParent(self):
        shutil.rmtree(MUTATOR_INPUT, ignore_errors=True)
        os.makedirs(MUTATOR_INPUT, exist_ok=True)
        shutil.copyfile(EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE, MUTATOR_CHEMISTRY_FILE)
        shutil.copyfile(EVOLVER_CHEMISTRY_PARAMETERS_FILE, MUTATOR_PARAMETERS_FILE)
        shutil.copyfile(EVOLVER_CHEMISTRY_RULES_FILE, MUTATOR_RULES_FILE)
        self.writeMutatorSpeciesFile(MUTATOR_SPECIES_FILE)
        runMutator()
        self.updateConcentrationsMutatedChemistry(MUTATOR_OUTPUT_FILE)
        formatFile(MUTATOR_OUTPUT_FILE)
        shutil.copyfile(MUTATOR_OUTPUT_FILE, EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE)
        shutil.copyfile(MUTATOR_OUTPUT_FILE, EVOLVER_CHEMISTRY_WITH_CONTAINER_FILE)
        shutil.copyfile(MUTATOR_OUTPUT_RULES_FILE, EVOLVER_CHEMISTRY_RULES_FILE)

    def initialize(self):
        os.makedirs(os.path.join(EVOLVER_INPUT, "chemistry_info"), exist_ok=True)
        self.copyChemistryFiles()
        raf = self.checkRAF(EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE)
        if raf:
            self.setParameters(EVOLVER_PARAMETERS_FILE)
            formatFile(EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE)
            catalysts = self.pickContainerCatalysts()
            self.setContainerCatalysts(catalysts)
            shutil.rmtree(PITZALIS_OUTPUT)
            os.makedirs(PITZALIS_OUTPUT)
        else:
            print(colored("LA CHIMICA NON CONTIENE RAF","red",attrs=['bold']))
            exit(0)

    def evolve(self):
        i = 0
        countReactions, countSpecies, countNotNullSpecies, introducedSpeciesName, introducedSpeciesType, timeRecords, acceptedStatus = [], [], [], [], [], [], []
        introducedSpeciesName.append("None")
        introducedSpeciesType.append("None")
        while i<self.getParameter("numberOfEvolutions"):
            self.addContainerSpecies(firstLap=(i==0))
            time = self.pitzalisSimulator()
            timeRecords.append(time)
            if time <= (self.getPreviousTime() + (self.getPreviousTime() * (self.getParameter("timeTolerance")/100))):
                self.setPreviousTime(time)
                self.setConcentrations(getSpeciesConcentrations(PITZALIS_QUANTITIES))
                acceptedStatus.append(True)
            else:
                acceptedStatus.append(False)
            species, notNullSpecies = countSpeciesFromPitzalis(getSpeciesConcentrations(PITZALIS_QUANTITIES))
            countNotNullSpecies.append(notNullSpecies)
            countSpecies.append(species)
            countReactions.append(getReactionsCountFromFile(EVOLVER_CHEMISTRY_WITHOUT_CONTAINER_FILE))
            self.mutateParent()
            type=self.getCurrentIntroducedSpecies()[0]['type']
            introducedSpecies = [d['name'] for d in self.getCurrentIntroducedSpecies()]
            introducedSpeciesName.append(introducedSpecies)
            introducedSpeciesType.append(type)
            i += 1
            directory = "data "+datetime.now().strftime("%d.%m")
            writeCSVEvolverAnalysis(i, countReactions, countSpecies, countNotNullSpecies, introducedSpeciesName, introducedSpeciesType, timeRecords, acceptedStatus, directory)
        countReactions.append(getReactionsCountFromFile(MUTATOR_OUTPUT_FILE))
        countSpecies.append(getSpeciesCountFromFile(MUTATOR_OUTPUT_FILE))
        countNotNullSpecies.append("None")
        timeRecords.append("None")
        acceptedStatus.append(None)
        directory = "data "+datetime.now().strftime("%d.%m")
        writeCSVEvolverAnalysis(i+1, countReactions, countSpecies, countNotNullSpecies, introducedSpeciesName, introducedSpeciesType, timeRecords, acceptedStatus, directory)
        writeExcelEvolverAnalysis(i+1, countReactions, countSpecies, countNotNullSpecies, introducedSpeciesName, introducedSpeciesType, timeRecords, acceptedStatus)
        introducedSpeciesType.append(type)

