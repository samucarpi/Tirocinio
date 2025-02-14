from utils.parser import *
from utils.utils import *
from species_generator.generator import Generator as speciesGenerator
import shutil

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
            if choice == "N":
                dir = os.path.join(BASE_DIR, "io", "launcher", "output", "series")
                count = 0
                while os.path.exists(os.path.join(dir, serieName)):
                    count += 1
                    serieName = self.getLauncherParameter("serieName")+"_"+str(count)
                newPath = os.path.join(BASE_DIR, "io", "launcher", "output", "series", serieName)
                os.makedirs(newPath, exist_ok=False)
                print(colored("Creata una nuova serie: "+serieName,"yellow"))
            else:
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
    
    def formatFile(self, path):
        with open(path, "r") as f:
            lines = f.readlines()
        formattedFile = [l for l in lines if l.strip() != "NESSUNA REAZIONE GENERATA, SI CONSIGLIA DI MODIFICARE I PARAMETRI"]
        formattedFile = formattedFile[2:]
        with open(path, "w") as f:
            f.writelines(formattedFile)

    def searchRaf(self, serieName, lap):
        seriePath = os.path.join(BASE_DIR, "io", "launcher", "output", "series", serieName, str(lap), "output", "output-uniqueReactions.txt")
        venturiPath = os.path.join(BASE_DIR, "utils", "venturi")
        copyInputDir = f'copy "{seriePath}" "{venturiPath}/In"'
        os.system(copyInputDir)
        uniqueReactionsPath = os.path.join(venturiPath, "In", "output-uniqueReactions.txt")
        self.formatFile(uniqueReactionsPath)
        executeVenturi = f'cd "{venturiPath}/CRST_src" && python ./Driver.py -v cta > nul 2>&1'
        os.system(executeVenturi)
        if os.listdir(venturiPath+"/Out"):
            print("Raf trovato")
        shutil.rmtree(venturiPath+"/Out/")
        

    def launch(self, loader):
        launches = self.getLauncherParameter("launches")
        serieName = self.getLauncherParameter("serieName")
        generatorParametersPath = os.path.join(BASE_DIR, "io/generator/input/parameters.txt")
        generatorParameters = readFile(generatorParametersPath)
        originalSeed = self.getGeneratorParameters()[7].strip()
        self.setGeneratorParameters(generatorParameters)
        serieName = self.createSerie(serieName)
        if self.getLauncherParameter("generateSpecies")=="ON":
            sGenerator = speciesGenerator(self.debug)
            sGenerator.initialization(self.getLauncherParameter("innerRadius"),self.getLauncherParameter("outerRadius"),self.getLauncherParameter("selectionProbability"))
            originalSpeciesPath = os.path.join(BASE_DIR,"io","generator","input","species.txt")
            speciesBackup = self.getSpecies(originalSpeciesPath)
        if not self.debug:
            loader.start("Lanci in corso")
        for i in range(launches):
            if self.getLauncherParameter("generateSpecies")=="ON":
                species = sGenerator.generateSpecies(speciesBackup)
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
            makeLapDir = "mkdir io\\launcher\\output\\series\\"+serieName+"\\%d"%(i+1)
            os.system(makeLapDir)
            makeInputDir = "mkdir io\\launcher\\output\\series\\"+serieName+"\\%d"%(i+1)+"\\input > nul 2>&1"
            makeOutputDir = "mkdir io\\launcher\\output\\series\\"+serieName+"\\%d"%(i+1)+"\\output > nul 2>&1"
            os.system(makeInputDir)
            os.system(makeOutputDir)
            copyInputDir = "copy io\\generator\\input\\*.* io\\launcher\\output\\series\\"+serieName+"\\%d"%(i+1)+"\\input > nul 2>&1"
            os.system(copyInputDir)
            copyOutputDir = "copy io\\generator\\output\\*.* io\\launcher\\output\\series\\"+serieName+"\\%d"%(i+1)+"\\output > nul 2>&1"
            os.system(copyOutputDir)
            if self.debug:
                print(colored("Copia dei file input/output completata","yellow"))
            self.searchRaf(serieName, i+1)
        self.writeNewSeed(originalSeed)
        self.writeNewSpecies(speciesBackup)
