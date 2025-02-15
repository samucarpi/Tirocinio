from utils.parser import *
from utils.utils import *
from utils.loader import Loader
from species_generator.generator import Generator as speciesGenerator

class Launcher:
    def __init__(self, debug):
        self.launcherParameters = None
        self.generatorParameters = None
        self.debug = debug

    def getGeneratorParameters(self):
        return self.generatorParameters
    
    def setGeneratorParameters(self, generatorParameters):
        self.generatorParameters = generatorParameters

    def getLauncherParameters(self):
        return self.launcherParameters

    def setLauncherParameters(self, launcherParameters):
        self.launcherParameters = launcherParameters

    def setLauncherParameter(self, parameter, value):
        self.launcherParameters[parameter] = value

    def getLauncherParameter(self, parameter):
        return self.launcherParameters[parameter]

    def initializeParameters(self):
        launcherError,launcherParameters = getLauncherParameters(BASE_DIR)
        if launcherError:
            for message in launcherParameters:
                print(colored(message,"red",attrs=['bold']))
            exit()
        else:
            self.setLauncherParameters(launcherParameters)
            generatorParametersPath = BASE_DIR+"/io/generator/input/parameters.txt"
            generatorParameters = readFile(generatorParametersPath)
            self.setGeneratorParameters(generatorParameters)

    def setSeed(self, seed):
        seed = generateSeed(seed)
        self.setLauncherParameter("seed", seed)

    def initialization(self):
        self.initializeParameters()
        self.setSeed(self.getLauncherParameter("seed"))

    def createSerie(self,serieName):
        path = os.path.join(BASE_DIR, "io", "launcher", "output", "series", serieName)
        try:
            os.makedirs(path, exist_ok=False)
        except FileExistsError:
            print(colored("La serie '"+serieName+"' è già esistente. Sovrascrivere? (Y,N)","red"))
            choice = input("Y/N: ")
            while choice not in ["Y","N","y","n"]:
                print(colored("Scelta non valida. Inserire Y o N","red"))
                choice = input("Y/N: ")
            if choice == "N":
                dir = os.path.join(BASE_DIR, "io", "launcher", "output", "series")
                count = 0
                while os.path.exists(os.path.join(dir, serieName)):
                    count += 1
                    serieName = self.getLauncherParameter("serieName")+"_"+str(count)
                newPath = os.path.join(BASE_DIR, "io", "launcher", "output", "series", serieName)
                os.makedirs(newPath, exist_ok=False)
                print(colored("Creata una nuova serie: "+serieName,"yellow"))
            elif choice == "Y":
                shutil.rmtree(path)
                os.makedirs(path, exist_ok=True)
                print(colored("Serie '"+serieName+"' sovrascritta","yellow"))
        else:
            if self.debug:
                print(colored("Creata una nuova serie: "+serieName,"yellow"))
        return serieName

    def writeNewSeed(self,seed):
        generatorParametersPath = os.path.join(BASE_DIR,"io","generator","input","parameters.txt")
        f = open(generatorParametersPath,"w")
        for i in range(len(self.getGeneratorParameters())):
            if i==7:
                f.write(str(seed)+"\n")
            else:
                f.write(self.getGeneratorParameters()[i])
        f.close()

    def getSpecies(self, path):
        species = readFile(path)
        species = [s.strip() for s in species if s.strip() != '' and s.strip()[0] != '#']
        return species

    def writeNewSpecies(self, species):
        speciesPath = os.path.join(BASE_DIR,"io","generator","input","species.txt")
        f = open(speciesPath,"w")
        f.write("# FILE DI INSERIMENTO DELLE SPECIE CHIMICHE INIZIALI\n\n# - SPECIES -\n")
        for s in species:
            f.write(s+"\n")
        f.close()

    def searchRAF(self, serieName, lap, loader):
        seriePath = os.path.join(BASE_DIR, "io", "launcher", "output", "series", serieName, str(lap), "output", "output-uniqueReactions.txt")
        venturiPath = os.path.join(BASE_DIR, "utils", "venturi")
        venturiInputPath = os.path.join(venturiPath, "In","output-uniqueReactions.txt")
        copyFile(seriePath, venturiInputPath)
        formatFileForVenturi(venturiInputPath)
        if self.debug:
            loader=Loader()
            loader.start("Ricerca di RAF in corso")
        runVenturi(venturiPath)
        if self.debug:
            loader.stop()
        venturiOutputPath = os.path.join(venturiPath, "Out")
        if os.listdir(venturiOutputPath):
            outPath = os.path.join(BASE_DIR, "io", "launcher", "output", "series", serieName, str(lap), "output")
            venturiOutputFilePath = os.path.join(venturiOutputPath, os.listdir(venturiOutputPath)[0])
            copyFile(venturiOutputFilePath, outPath)
            if self.debug:
                print(colored("RAF individuato","green",attrs=['underline']))
            shutil.rmtree(venturiOutputPath)
            os.makedirs(venturiOutputPath)
        else:
            if self.debug:
                print(colored("RAF non individuato","red",attrs=['underline']))

    def launch(self):
        launches = self.getLauncherParameter("launches")
        serieName = self.getLauncherParameter("serieName")
        generatorParametersPath = os.path.join(BASE_DIR, "io/generator/input/parameters.txt")
        generatorParameters = readFile(generatorParametersPath)
        originalSeed = self.getGeneratorParameters()[7].strip()
        self.setGeneratorParameters(generatorParameters)
        serieName = self.createSerie(serieName)
        loader=Loader()
        if self.getLauncherParameter("generateSpecies")=="ON":
            sGenerator = speciesGenerator(self.debug)
            sGenerator.initialization(self.getLauncherParameter("innerRadius"),self.getLauncherParameter("outerRadius"),self.getLauncherParameter("selectionProbability"))
            originalSpeciesPath = os.path.join(BASE_DIR,"io","generator","input","species.txt")
            originalSpecies = self.getSpecies(originalSpeciesPath)
        if not self.debug:
            loader.start("Lanci in corso")
        for i in range(launches):
            if self.getLauncherParameter("generateSpecies")=="ON":
                species = sGenerator.generateSpecies(originalSpecies)
                self.writeNewSpecies(species)
            if not self.getLauncherParameter("seed") or i>0:
                self.setLauncherParameter("seed", getRandomValue())
            if self.debug:
                print(colored("Lancio "+str(i+1),"cyan",attrs=['bold']))
                print(colored("Seed: "+str(self.getLauncherParameter("seed")),"dark_grey"))
            self.writeNewSeed(self.getLauncherParameter("seed"))
            os.system("python main.py generate > nul 2>&1")
            if self.debug:
                print(colored("Generazione completata","green"))
            lapPath = os.path.join(BASE_DIR, "io", "launcher", "output", "series", serieName, "%d"%(i+1))
            createDirectory(lapPath)
            inputPath = os.path.join(lapPath, "input")
            createDirectory(inputPath)
            outputPath = os.path.join(lapPath, "output")
            createDirectory(outputPath)
            inputGeneratorPath = os.path.join(BASE_DIR, "io", "generator", "input", "*.*")
            copyInputDir = "copy "+inputGeneratorPath+" "+inputPath+" > nul 2>&1"
            os.system(copyInputDir)
            outputGeneratorPath = os.path.join(BASE_DIR, "io", "generator", "output", "*.*")
            copyOutputDir = "copy "+outputGeneratorPath+" "+outputPath+" > nul 2>&1"
            os.system(copyOutputDir)
            if self.debug:
                print(colored("Copia dei file input/output completata","yellow"))
            self.searchRAF(serieName, i+1, loader)
        self.writeNewSeed(originalSeed)
        if self.getLauncherParameter("generateSpecies")=="ON":
            self.writeNewSpecies(originalSpecies)
        if not self.debug:
            loader.stop()
