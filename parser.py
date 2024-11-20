from objects.species import Species

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
    return parameters

def newSpecies(species):
    return Species(species, True)

