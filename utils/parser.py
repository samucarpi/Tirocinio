from generator.objects.species import Species
from tabulator.objects.rule import Rule
from utils.utils import *

def parseInputSpecies(inputFile):
    speciesObj=[]
    data=getFileData(inputFile)
    for species in data:
        speciesObj.append(createSpeciesObject(species))
    return speciesObj

def getFileData(inputFile):
    data=[]
    with open(inputFile) as f:
        lines=[line.strip() for line in f if line.strip()]
        for line in lines:
            if not line.startswith("#"):
                data.append(line.strip())
    return data

def checkIntData(data, title):
    try:
        parameter = int(data)
        if parameter>=0:
            return True, ""
        else:
            return False, title+" deve essere >= 0"
    except:
        return False, title+" non è numerico"

def checkFloatData(data, title):
    try:
        parameter = float(data)
        if parameter>=0:
            return True, ""
        else:
            return False, title+" deve essere >= 0"
    except:
        return False, title+" non è numerico"
    
def checkOnOffData(data, title):
    data = data.upper()
    if data=="ON" or data=="OFF":
        return True, ""
    else:
        return False, title+" deve essere ON o OFF"
    
def checkFileData(data, title):
    if data.endswith(".txt"):
        return True, ""
    else:
        return False, title+" deve terminare con .txt"

def getParameters(input_file, species, speciesGeneration=False):
    parameters={}
    error=False
    errorMessages=[]
    with open(input_file) as f:
        lines = [line.strip() for line in f if line.strip()]
        for i, line in enumerate(lines):
            match(line):
                case "- SEED -":
                    if lines[i+1].isdigit():
                        parameters['seed']=int(lines[i+1])
                    elif lines[i+1]=="None":
                        parameters['seed']=None
                    else:
                        error=True
                        errorMessages.append("Seed non valido")
                case "- MONOMERI E COMPLEMENTARI -":
                    i=i+1
                    items=[]
                    while lines[i]!="- LIMITE INFERIORE PER ESSERE CATALIZZATORE -":
                        items.append(lines[i].split())
                        i=i+1
                    data=[[c.strip(',') for c in i] for i in items]
                    monomers = []
                    speciesMonomers = []
                    for s in species:
                        for c in s.name:
                            if c not in speciesMonomers:
                                speciesMonomers.append(c)
                    for d in data:
                        if d[0] not in speciesMonomers and not speciesGeneration:
                            error=True
                            errorMessages.append(f"{d[0]} monomero non presente tra le specie")
                        monomer = {}
                        monomer["name"]=d[0]
                        monomer["complementary"]=d[1]
                        monomers.append(monomer)
                    parameters['monomers']=monomers
                case "- PROBABILITA DI CATALIZZAZIONE -":
                    result = checkFloatData(lines[i+1], "- PROBABILITA DI CATALIZZAZIONE -")
                    if result[0]:
                        parameters['probabilityOfCatalyst']=float(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- LIMITE INFERIORE PER ESSERE CATALIZZATORE -":
                    result = checkIntData(lines[i+1], "- LIMITE INFERIORE PER ESSERE CATALIZZATORE -")
                    if result[0]:
                        parameters['lowerLimitForCatalyst']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- CATALIZZATORI PER CONDENSAZIONI INIZIALI -":
                    result = checkIntData(lines[i+1], "- CATALIZZATORI PER CONDENSAZIONI INIZIALI -")
                    if result[0]:
                        parameters['initialCondensationCatalysts']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- CATALIZZATORI PER CLEAVAGE INIZIALI -":
                    result = checkIntData(lines[i+1], "- CATALIZZATORI PER CLEAVAGE INIZIALI -")
                    if result[0]:
                        parameters['initialCleavageCatalysts']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- PROBABILITA DI ESSERE CLEAVAGE -":
                    result = checkFloatData(lines[i+1], "- PROBABILITA DI ESSERE CLEAVAGE -")
                    if result[0]:
                        parameters['probabilityOfCleavage']=float(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- MINIMA LUNGHEZZA DEL SITO ATTIVO -":
                    result = checkIntData(lines[i+1], "- MINIMA LUNGHEZZA DEL SITO ATTIVO -")
                    if result[0]:
                        parameters['minActiveSiteLength']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- MASSIMA LUNGHEZZA DEL SITO ATTIVO -":
                    result = checkIntData(lines[i+1], "- MASSIMA LUNGHEZZA DEL SITO ATTIVO -")
                    if result[0]:
                        parameters['maxActiveSiteLength']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                    if parameters['maxActiveSiteLength']<parameters['minActiveSiteLength']:
                        error=True
                        errorMessages.append("La lunghezza massima del sito attivo deve essere >= della lunghezza minima")
                case "- MASSIMA LUNGHEZZA PER CONDENSAZIONI -":
                    result = checkIntData(lines[i+1], "- MASSIMA LUNGHEZZA PER CONDENSAZIONI -")
                    if result[0]:
                        parameters['maxCondensationLength']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- LUNGHEZZA MASSIMA PER CLEAVAGE -":
                    result = checkOnOffData(lines[i+1], "- LUNGHEZZA MASSIMA PER CLEAVAGE -")
                    if result[0]:
                        parameters['maxCleavageLength']=lines[i+1]
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- LUNGHEZZA MASSIMA PER CATALIZZATORE -":
                    result = checkOnOffData(lines[i+1], "- LUNGHEZZA MASSIMA PER CATALIZZATORE -")
                    if result[0]:
                        parameters['maxCatalystLength']=lines[i+1]
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- TEMPO MASSIMO DI GENERAZIONE -":
                    result = checkFloatData(lines[i+1], "- TEMPO MASSIMO DI GENERAZIONE -")
                    if result[0]:
                        parameters['maxGenerationTime']=lines[i+1]
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- MASSIMA LUNGHEZZA PER IL PASSAGGIO DELLA MEMBRANA -":
                    result = checkIntData(lines[i+1], "- MASSIMA LUNGHEZZA PER IL PASSAGGIO DELLA MEMBRANA -")
                    if result[0]:
                        parameters['maxMembraneLength']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- NOME DEL FILE DI OUTPUT -":
                        parameters['outputFile']=lines[i+1]
                case "- NOME DEL FILE DI OUTPUT DELLE REGOLE -":
                    result = checkFileData(lines[i+1], "- NOME DEL FILE DI OUTPUT DELLE REGOLE -")
                    if result[0]:
                        parameters['outputRulesFile']=lines[i+1]
                    else:
                        error=True
                        errorMessages.append(result[1])

    if parameters['lowerLimitForCatalyst'] < parameters['minActiveSiteLength']:
        error=True
        errorMessages.append("Il limite inferiore per essere catalizzatore deve essere >= della lunghezza minima del sito attivo")
        
    if error:
        return error, errorMessages
    else:
        return error, parameters

def createSpeciesObject(species):
    return Species(species)

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

def getLauncherParameters():
    parameters={}
    error=False
    errorMessages=[]
    with open(LAUNCHER_PARAMETERS_FILE) as f:
        lines = [line.strip() for line in f if line.strip()]
        for i, line in enumerate(lines):
            match(line):
                case "- NUMERO DI LANCI -":
                    result = checkIntData(lines[i+1], "- NUMERO DI LANCI -")
                    if result[0]:
                        parameters['launches']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- NOME DELLA SERIE -":
                    parameters['serieName']=lines[i+1]
                case "- SEED INIZIALE -":
                    if lines[i+1].isdigit():
                        parameters['seed']=int(lines[i+1])
                    elif lines[i+1]=="None":
                        parameters['seed']=None
                    else:
                        error=True
                        errorMessages.append("Numero del seed non valido")
                case "- RICERCA RAF -":
                    result = checkOnOffData(lines[i+1], "- RICERCA RAF -")
                    if result[0]:
                        parameters['rafSearch']=lines[i+1]
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- GENERAZIONE SPECIE -":
                    result = checkOnOffData(lines[i+1], "- GENERAZIONE SPECIE -")
                    if result[0]:
                        parameters['generateSpecies']=lines[i+1]
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- RAGGIO INTERNO -":
                    result = checkIntData(lines[i+1], "- RAGGIO INTERNO -")
                    if result[0]:
                        parameters['innerRadius']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- RAGGIO ESTERNO -":
                    result = checkIntData(lines[i+1], "- RAGGIO ESTERNO -")
                    if result[0]:
                        parameters['outerRadius']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- PROBABILITA DI SELEZIONE -":
                    result = checkFloatData(lines[i+1], "- PROBABILITA DI SELEZIONE -")
                    if result[0]:
                        parameters['selectionProbability']=float(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
    if parameters['outerRadius']<parameters['innerRadius']:
        error=True
        errorMessages.append("Il raggio esterno deve essere >= del raggio interno")
    if error:
        return error, errorMessages
    else:
        return error, parameters

def getKauffmanGeneratorParameters(path):
    parameters={}
    error=False
    errorMessages=[]
    with open(path) as f:
        lines = [line.strip() for line in f if line.strip()]
        for i, line in enumerate(lines):
            match(line):
                case "- SEED -":
                    if lines[i+1].isdigit():
                        parameters['seed']=int(lines[i+1])
                    elif lines[i+1]=="None":
                        parameters['seed']=None
                    else:
                        error=True
                        errorMessages.append("Seed non valido")
                case "- MONOMERI -":
                    data = lines[i+1].strip()
                    monomers = [m.strip() for m in data.split(",")]
                    if all(len(m) == 1 and m.isalpha() for m in monomers):
                        parameters['monomers'] = monomers
                    else:
                        error=True
                        errorMessages.append("Monomeri non validi")
                case "- LIMITE INFERIORE PER ESSERE CATALIZZATORE -":
                    result = checkIntData(lines[i+1], "- LIMITE INFERIORE PER ESSERE CATALIZZATORE -")
                    if result[0]:
                        parameters['lowerLimitForCatalyst']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- PROBABILITA DI ESSERE CLEAVAGE -":
                    result = checkFloatData(lines[i+1], "- PROBABILITA DI ESSERE CLEAVAGE -")
                    if result[0]:
                        parameters['probabilityOfCleavage']=float(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- TEMPO MASSIMO DI GENERAZIONE -":
                    result = checkFloatData(lines[i+1], "- TEMPO MASSIMO DI GENERAZIONE -")
                    if result[0]:
                        parameters['maxGenerationTime']=lines[i+1]
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- LUNGHEZZA MASSIMA DEL PRODOTTO -":
                    result = checkIntData(lines[i+1], "- LUNGHEZZA MASSIMA DEL PRODOTTO -")
                    if result[0]:
                        parameters['maxProductLength']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- LIMITE DI REAZIONI -":
                    result = checkIntData(lines[i+1], "- LIMITE DI REAZIONI -")
                    if result[0]:
                        parameters['maxReactionProduced']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- MASSIMA LUNGHEZZA PER IL PASSAGGIO DELLA MEMBRANA -":
                    result = checkIntData(lines[i+1], "- MASSIMA LUNGHEZZA PER IL PASSAGGIO DELLA MEMBRANA -")
                    if result[0]:
                        parameters['maxMembraneLength']=int(lines[i+1])
                    else:
                        error=True
                        errorMessages.append(result[1])
                case "- NOME DEL FILE DI OUTPUT -":
                        parameters['outputFile']=lines[i+1]
    if error:
        return error, errorMessages
    else:
        return error, parameters