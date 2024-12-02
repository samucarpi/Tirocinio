import random,sys,os
from tabulate import tabulate
from termcolor import colored

# Constants
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

# Random functions
def generateSeed(seed):
    if seed:
        random.seed(seed)
    else:
        seed = random.randrange(sys.maxsize)
        random.seed(seed)
    return seed

def calculateProbability(probability):
    return (random.random() < probability)

def calculateRandomValue(minValue, maxValue):
    return random.randint(minValue, maxValue)

def calculateActiveSiteLength(catalyst, minActiveSiteLength, maxActiveSiteLength):
    length=calculateRandomValue(minActiveSiteLength, maxActiveSiteLength)
    while len(catalyst.getName()) < length:
        length=calculateRandomValue(minActiveSiteLength, maxActiveSiteLength)
    return length

# Aesthetic functions
def underlinedHeader(headers):
    headers = [underlinedPrint(header) for header in headers]
    return headers

def underlinedPrint(text):
    return (colored(text,attrs=['underline']))

def boldTitle(text):
    return (colored(text,'blue',attrs=['bold','underline']))

def boldGreenTitle(text):
    return (colored(text,'green',attrs=['bold','underline']))

def error(text):
    return (colored(text,'red',attrs=['bold']))

# Debug print functions
def printParameters(parameters):
    print(boldTitle("\nPARAMETRI"))
    if not parameters:
        print(error("NESSUN PARAMETRO PRESENTE"))
        return
    catalystsParam=["probabilityOfCatalyst","lowerLimitForCatalyst","initialCondensationCatalysts","initialCleavageCatalysts"]
    printSelectedParameters("CATALIZZATORI",parameters, catalystsParam)
    reactionsParam=["probabilityOfCleavage","minActiveSiteLength","maxActiveSiteLength","maxCondensationLength","maxCleavageLength","maxCatalystLength"]
    printSelectedParameters("REAZIONI",parameters, reactionsParam)

def printSelectedParameters(title, parameters, selectedParameters):
    print(colored(title,'light_green',attrs=['dark']))
    headers = ["PARAMETRO", "VALORE"]
    table=[]
    for p in selectedParameters:
        table.append([p,parameters[p]])
    print(tabulate(table, underlinedHeader(headers), tablefmt="simple_grid"))

def printSpecies(species,ended=False):
    if not species:
        print(error("NESSUNA SPECIE PRESENTE"))
        return
    headers = ["SPECIE", "INIZIALI"]
    table = [[s.name, "Sì" if s.isInitial else "No"] for s in species]
    if not ended:
        print(boldTitle("SPECIE"))
    else:
        print(boldGreenTitle("SPECIE GENERATE"))
    print(tabulate(table, underlinedHeader(headers), tablefmt="simple_grid"))

def printReactionClasses(reactionClasses,new=False):
    if not reactionClasses:
        print(error("NESSUNA CLASSE DI REAZIONE PRESENTE"))
        return
    headers = ["SPECIE", "TIPO", "SITO ATTIVO", "POSIZIONE", "REAZIONE"]
    table = []
    for rc in reactionClasses:
        if rc.getCatalyst().getIsCondensation():
            table.append([rc.getCatalyst().name, 'Condensazione', rc.getCatalyst().getName()[rc.getStart():rc.getEnd()],rc.getSplit(),'R-'+rc.getReagents()[0]+'  '+rc.getReagents()[1]+'-R'])
        else:
            table.append([rc.getCatalyst().name, 'Cleavage', rc.getCatalyst().getName()[rc.getStart():rc.getEnd()],rc.getSplit(), 'R-'+rc.getReagents()[0]+'-R'])
    if not new: 
        print(boldTitle("CLASSI DI REAZIONI"))
    else: 
        print(boldTitle("NUOVE CLASSI GENERATE"))
    print(tabulate(table, underlinedHeader(headers), tablefmt="simple_grid"))

def printReactions(reactions):
    if not reactions:
        print(error("NESSUNA REAZIONE PRESENTE"))
        print(error("PER GENERARE LE REAZIONI MODIFICARE I PARAMETRI"))
        return
    print(boldGreenTitle("REAZIONI GENERATE"))
    for r in reactions:
        if r.getReactionClass().getCatalyst().getIsCondensation():
            print(r.getReactants()[0]+" + "+r.getReactants()[1]+" + "+r.getReactants()[2]+" --> "+r.getProducts()[0]+" + "+r.getProducts()[1])
        else:
            print(r.getReactants()[0]+" + "+r.getReactants()[1]+" --> "+r.getProducts()[0]+" + "+r.getProducts()[1]+" + "+r.getProducts()[2])

# Output print functions
def writeOutputFile(seed,parameters,species,reactions):
    print(boldTitle("SEED UTILIZZATO: "+str(seed)))
    path = os.path.join(BASE_DIR, "IOfiles/output/"+parameters['outputFile'])
    with open(path, 'w') as f:
        f.write(f"SEED UTILIZZATO: {seed}\n\n")
        f.write((f"{"Cont":<15}{'1.35e-16':<10}{"0.0":<10}\n"))
        sortedSpecies=sorted(species,key=len)
        crossMembraneSpecies=[]
        for s in sortedSpecies:
            if len(s.getName())>parameters['maxMembraneLength']:
                val="0.01"
            else:
                val="0.0"
                crossMembraneSpecies.append(s)
            f.write(f"{s.getName():<15}{'1e-15':<10}{val:<10}\n")
        f.write("\n")
        for s in crossMembraneSpecies:
            f.write(f"{10.0} > {s.getName()} ; 1.00E-18\n")
        if not reactions:
            f.write("NESSUNA REAZIONE GENERATA, SI CONSIGLIA DI MODIFICARE I PARAMETRI\n")
        else:
            for r in reactions:
                if r.getReactionClass().getCatalyst().getIsCondensation():
                    f.write(f"{r.getReactants()[0]} + {r.getReactants()[1]} + {r.getReactants()[2]} > {r.getProducts()[0]} + {r.getProducts()[1]} ; 0.1"+"\n")
                else:
                    f.write(f"{r.getReactants()[0]} + {r.getReactants()[1]} > {r.getProducts()[0]} + {r.getProducts()[1]} + {r.getProducts()[2]} ; 0.1"+"\n")