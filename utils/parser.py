from generator.objects.species import Species
from tabulator.objects.rule import Rule
from utils.utils import *

def parseInputSpecies(inputFile):
    speciesObj=[]

    data=getFileData(inputFile)
    for species in data:
        speciesObj.append(newSpecies(species))

    return speciesObj

def getFileData(inputFile):
    data=[]
    with open(inputFile) as f:
        lines=[line.strip() for line in f if line.strip()]
        for line in lines:
            if not line.startswith("#"):
                data.append(line.strip())
    return data

def getParameters(input_file):
    parameters={}
    with open(input_file) as f:
        lines = [line.strip() for line in f if line.strip()]
        for i, line in enumerate(lines):
            match(line):
                case "- SEED -":
                    if lines[i+1].isdigit():
                        parameters['seed']=int(lines[i+1])
                    else:
                        parameters['seed']=None
                case "- PROBABILITA DI CATALIZZAZIONE -":
                    parameters['probabilityOfCatalyst']=float(lines[i+1])
                case "- LIMITE INFERIORE PER ESSERE CATALIZZATORE -":
                    parameters['lowerLimitForCatalyst']=int(lines[i+1])
                case "- CATALIZZATORI PER CONDENSAZIONI INIZIALI -":
                    parameters['initialCondensationCatalysts']=int(lines[i+1])
                case "- CATALIZZATORI PER CLEAVAGE INIZIALI -":
                    parameters['initialCleavageCatalysts']=int(lines[i+1])
                case "- PROBABILITA DI ESSERE CLEAVAGE -":
                    parameters['probabilityOfCleavage']=float(lines[i+1])
                case "- MINIMA LUNGHEZZA DEL SITO ATTIVO -":
                    parameters['minActiveSiteLength']=int(lines[i+1])
                case "- MASSIMA LUNGHEZZA DEL SITO ATTIVO -":
                    parameters['maxActiveSiteLength']=int(lines[i+1])
                case "- MASSIMA LUNGHEZZA PER CONDENSAZIONI -":
                    parameters['maxCondensationLength']=int(lines[i+1])
                case "- LUNGHEZZA MASSIMA PER CLEAVAGE -":
                    parameters['maxCleavageLength']=lines[i+1]
                case "- LUNGHEZZA MASSIMA PER CATALIZZATORE -":
                    parameters['maxCatalystLength']=lines[i+1]
                case "- NOME DEL FILE DI OUTPUT -":
                    if lines[i+1].endswith(".txt"):
                        parameters['outputFile']=lines[i+1]
                    else:
                        parameters['outputFile']=None
                case "- MASSIMA LUNGHEZZA PER IL PASSAGGIO DELLA MEMBRANA -":
                    parameters['maxMembraneLength']=int(lines[i+1])
                case "- NOME DEL FILE DI OUTPUT DELLE REGOLE -":
                    if lines[i+1].endswith(".txt"):
                        parameters['outputRulesFile']=lines[i+1]
                    else:
                        parameters['outputRulesFile']=None
    return parameters

def newSpecies(species):
    return Species(species, True)

def getObjects(BASE_DIR):
    try:
        path = os.path.join(BASE_DIR, "io/Tabulator/input/chemistry.txt")
        species = []
        reactions = []
        with open(path, 'r') as f:
            lines = f.readlines()
            counter = 0
            for line in lines:
                if not line.strip():
                    counter+=1
                    continue
                if counter == 1:
                    line=line.split()[0]
                    species.append(line)
                if counter == 2:
                    if '+' in line:
                        reactions.append(line.strip())
        return species,reactions
    except:
        print("Impossibile aprire il file")

def getRules(BASE_DIR):
    try:
        path = os.path.join(BASE_DIR, "io/Tabulator/input/chemistryRules.txt")
        rules = []
        with open(path, 'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            lines = lines[1:]
            for line in lines:
                line = line.split()
                rule = Rule(line[0],line[1],line[2],line[3],line[4])
                rules.append(rule)
        return rules
    except:
        return []
