import random,sys,os,shutil,re
from tabulate import tabulate
from termcolor import colored
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

# Constants
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
GENERATOR_PARAMETERS_FILE = os.path.join(BASE_DIR, "io","generator","input","parameters.txt")
GENERATOR_SPECIES_FILE = os.path.join(BASE_DIR, "io","generator","input","species.txt")

# Utils functions
def readFile(path):
    f=open(path)
    file=f.readlines()
    f.close()
    return file

def getRandomValue():
    return random.randrange(sys.maxsize)

def copyFile(source,destination):
    shutil.copy(source,destination)

def formatFileForVenturi (path):
    with open(path, "r") as f:
        lines = f.readlines()
    formattedFile = [l for l in lines if l.strip() != "NESSUNA REAZIONE GENERATA, SI CONSIGLIA DI MODIFICARE I PARAMETRI"]
    formattedFile = formattedFile[2:]
    with open(path, "w") as f:
        f.writelines(formattedFile)

def createDirectory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def runVenturi(venturiPath):
    os.system(f'cd "{venturiPath}/CRST_src" && python ./Driver.py cta > nul 2>&1')

# Random functions
def generateSeed(seed):
    if seed:
        random.seed(seed)
    else:
        seed=getRandomValue()
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
    headers = ["SPECIE", "TIPO", "SITO ATTIVO", "POSIZIONE", "CLASSE"]
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

def orderCatalysts(catalysts):
        catalysts = sorted(catalysts, key=lambda x: x.getLength())
        return catalysts

def printTabulatedCatalysts(catalysts):
    for c in catalysts:
        print(c.getName(), c.getLength(), c.getTotalRules(), c.getCondensationRules(), c.getCleavageRules(), c.getTotalReactions(), c.getCondensationReactions(), c.getCleavageReactions(), c.getCatalyzerAsReagent(), c.getNumberOfCatalyzedSpecies(), c.getCatalyzedSpecies())

def printTabulatedSpecies(species):
        for s in species:
            print(s.getName(), s.getLength(), s.getTotalProducts(), s.getCondensationProducts(), s.getCleavageProducts(), s.getTotalCatalyzers(), s.getCondensationCatalyzers(), s.getCleavageCatalyzers(), s.getCatalyzers(), s.getSpeciesAsReactar())

# Output print functions
def deleteReportFile():
    file=os.path.join(BASE_DIR, "io/Generator/output/report.txt")
    if os.path.exists(file):
        os.remove(file)

def writeReportFile(seed,parameters,species,data):
    file=os.path.join(BASE_DIR, "io/Generator/output/report.txt")
    with open(file, 'w') as f:
        f.write("PARAMETRI\n")
        for key in parameters:
            f.write(f"{key}: {parameters[key]}\n")
        f.write("\n")
        type=data["error"]
        f.write("DATI\n")
        if type=="START":
            f.write("Numero di giri svolti completamente: "+str(data["lap"])+"\n")
            f.write("Non sono stati interrotti i processi di sviluppo di nuove reazioni o specie\n")
        if type=="REACTION":
            f.write("Numero di giri svolti completamente: "+str(data["lap"])+"\n")
            f.write("Generazione interrotta al giro "+str(data["lap"]+1)+" durante lo sviluppo di nuove reazioni\n")
            remainingReactions = len(data["reactionClasses"])-len(data["processedReactionClasses"])
            f.write("Ci sono ancora "+str(remainingReactions)+" classi di reazioni da analizzare: \n")
            for rc in data["reactionClasses"]:
                if rc in data["processedReactionClasses"]:
                    f.write(rc.printReactionClass()+"\n")
                else:
                    f.write(rc.printReactionClass()+" <--\n")
        if type=="SPECIES":
            f.write("Numero di giri svolti completamente: "+str(data["lap"])+"\n")
            f.write("Generazione interrotta al giro "+str(data["lap"]+1)+" durante la ricerca di nuove specie\n")
            remainingReactions = len(data["reactions"])-len(data["processedReactions"])
            f.write("Ci sono ancora "+str(remainingReactions)+" reazioni da analizzare: \n")
            for r in data["reactions"]:
                if r in data["processedReactions"]:
                    f.write(r.printReaction()+"\n")
                else:
                    f.write(r.printReaction()+" <--\n")
                

def writeOutputFile(seed,parameters,species,allReactions,uniqueReactions):
    allReactionsFile = os.path.join(BASE_DIR, "io/Generator/output/"+parameters['outputFile']+"-allReactions.txt")
    uniqueReactionsFile = os.path.join(BASE_DIR, "io/Generator/output/"+parameters['outputFile']+"-uniqueReactions.txt")
    multiplicyReactionsFile = os.path.join(BASE_DIR, "io/Generator/output/"+parameters['outputFile']+"-multiplicyReactions.txt")
    for file in [allReactionsFile, uniqueReactionsFile, multiplicyReactionsFile]:
        with open(file, 'w') as f:
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
            if file == allReactionsFile:   
                if not allReactions:
                    f.write("NESSUNA REAZIONE GENERATA, SI CONSIGLIA DI MODIFICARE I PARAMETRI\n")
                else:
                    for r in allReactions:
                        if r.getReactionClass().getCatalyst().getIsCondensation():
                            f.write(f"{r.getReactants()[0]} + {r.getReactants()[1]} + {r.getReactants()[2]} > {r.getProducts()[0]} + {r.getProducts()[1]} ; 0.1"+"\n")
                        else:
                            f.write(f"{r.getReactants()[0]} + {r.getReactants()[1]} > {r.getProducts()[0]} + {r.getProducts()[1]} + {r.getProducts()[2]} ; 0.1"+"\n")
            if file == uniqueReactionsFile:
                if not uniqueReactions:
                    f.write("NESSUNA REAZIONE GENERATA, SI CONSIGLIA DI MODIFICARE I PARAMETRI\n")
                else:
                    for r in uniqueReactions:
                        if r.getReactionClass().getCatalyst().getIsCondensation():
                            f.write(f"{r.getReactants()[0]} + {r.getReactants()[1]} + {r.getReactants()[2]} > {r.getProducts()[0]} + {r.getProducts()[1]} ; 0.1"+"\n")
                        else:
                            f.write(f"{r.getReactants()[0]} + {r.getReactants()[1]} > {r.getProducts()[0]} + {r.getProducts()[1]} + {r.getProducts()[2]} ; 0.1"+"\n")
            if file == multiplicyReactionsFile:
                if not uniqueReactions:
                    f.write("NESSUNA REAZIONE GENERATA, SI CONSIGLIA DI MODIFICARE I PARAMETRI\n")
                else:
                    for r in uniqueReactions:
                        multiplicity = r.getMultiplicity()
                        if r.getReactionClass().getCatalyst().getIsCondensation():
                            f.write(f"{str(multiplicity)+"x":<2} {r.getReactants()[0]} + {r.getReactants()[1]} + {r.getReactants()[2]} > {r.getProducts()[0]} + {r.getProducts()[1]} ; 0.1"+"\n")
                        else:
                            f.write(f"{str(multiplicity)+"x":<2} {r.getReactants()[0]} + {r.getReactants()[1]} > {r.getProducts()[0]} + {r.getProducts()[1]} + {r.getProducts()[2]} ; 0.1"+"\n")

def writeRulesFile(parameters,reactionClasses):
    path = os.path.join(BASE_DIR, "io/Generator/output/"+parameters['outputRulesFile'])
    with open(path, 'w') as f:
        f.write(f"{"CATALIZZATORE":<15} {"TIPO":<17} {"SITO ATTIVO":<13} {"POSIZIONE":<11} {"CLASSE":<10}\n")
        for rc in reactionClasses:
            if rc.getCatalyst().getIsCondensation():
                f.write(f"{rc.getCatalyst().getName():<15} {'Condensazione':<17} {rc.getCatalyst().getName()[rc.getStart():rc.getEnd()]:<13} {rc.getSplit():<11} {'R-'+rc.getReagents()[0]+'+'+rc.getReagents()[1]+'-R':<10}\n")
            else:
                f.write(f"{rc.getCatalyst().getName():<15} {'Cleavage':<17} {rc.getCatalyst().getName()[rc.getStart():rc.getEnd()]:<13} {rc.getSplit():<11} {'R-'+rc.getReagents()[0][:rc.getSplit()]+' '+rc.getReagents()[0][rc.getSplit():]+'-R':<10}\n")

def duplicateFilesForTabulator(parameters):
    shutil.copy(os.path.join(BASE_DIR,"io/Generator/output/"+parameters['outputFile']+"-uniqueReactions.txt"),os.path.join(BASE_DIR,"io/Tabulator/input/chemistry.txt"))
    shutil.copy(os.path.join(BASE_DIR,"io/Generator/output/"+parameters['outputRulesFile']),os.path.join(BASE_DIR,"io/Tabulator/input/chemistryRules.txt"))

def cleanReaction(reaction):
    formatted = re.sub(r'[^A-Za-z+]','',reaction)
    return formatted.split('+')

def setTable(pd, rows, columns):
    df = pd.DataFrame(rows, columns=columns)
    return df

def setTitle(ws, title, startRow, startCol, endCol):
    ws[f"{get_column_letter(startCol)}{startRow}"] = title
    ws[f"{get_column_letter(startCol)}{startRow}"].font = Font(size=14, bold=True)
    ws[f"{get_column_letter(startCol)}{startRow}"].alignment = Alignment(horizontal="center")
    ws[f"{get_column_letter(startCol)}{startRow}"].fill = PatternFill(start_color="d3d3d3", end_color="d3d3d3", fill_type="solid")
    ws[f"{get_column_letter(startCol)}{startRow}"].border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    ws.merge_cells(start_row=startRow, start_column=startCol, end_row=startRow, end_column=endCol)

def setTableStyle(ws, start_row, columns, df, border, color1, color2):
    for i, row in enumerate(ws.iter_rows(min_row=start_row, max_row=start_row+len(df), min_col=2, max_col=2+len(columns)-1), start=1):
        if i % 2 != 0:
            fill = color1 
        else:
            fill = color2
        for cell in row:
            cell.border = border
            cell.fill = fill
            cell.alignment = Alignment(wrap_text=True, vertical='center')
            cell.alignment = Alignment(vertical='center')

def resizeCells(ws, titles, catalystsColumns, speciesColumns):
    for col in ws.iter_cols():
        maxLength = 0
        column = col[0].column_letter
        for cell in col:
            if cell.value and isinstance(cell.value, str):
                if cell.value in titles:
                    continue
                if cell.value in catalystsColumns or cell.value in speciesColumns:
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                maxLength = max(maxLength, len(cell.value))
        width = min(maxLength+2, 30)
        ws.column_dimensions[column].width = width

def writeOnExcelFile(catalysts,species):
    catalystColumns = ['Name', 'Length', 'Reaction class', 'Condensation class', 'Cleavage class', 'Total generated reactions', 'Generated condensation reactions', 'Generated cleavage reactions', 'Catalyzers as reagent', 'Species catalized', 'Nr. species catalized']
    catalystRows = []
    for c in catalysts:
        catalystRows.append([c.getName(), c.getLength(), c.getTotalRules(), c.getCondensationRules(),c.getCleavageRules(), c.getTotalReactions(), c.getCondensationReactions(),c.getCleavageReactions(), c.getCatalyzerAsReagent(), c.getCatalyzedSpecies(), c.getNumberOfCatalyzedSpecies()])
    catalystDf = setTable(pd, catalystRows, catalystColumns)

    speciesColumns = ['Name', 'Length', 'Reaction as product', 'Condensation as products', 'Cleavage as products', 'Total catalyzers', 'Condensation catalyzers', 'Cleavage catalyzers', 'Catalyzers', 'Reactions as reactants']
    speciesRows = []
    for s in species:
        speciesRows.append([s.getName(), s.getLength(), s.getTotalProducts(), s.getCondensationProducts(),s.getCleavageProducts(), s.getTotalCatalyzers(), s.getCondensationCatalyzers(),s.getCleavageCatalyzers(), s.getCatalyzers(), s.getSpeciesAsReactar()])
    speciesDf = setTable(pd, speciesRows, speciesColumns)

    catalyzerAsSpeciesRows=[]
    for s in species:
        for c in catalysts:
            if c.getName() == s.getName():
                catalyzerAsSpeciesRows.append([s.getName(), s.getLength(), s.getTotalProducts(), s.getCondensationProducts(),s.getCleavageProducts(), s.getTotalCatalyzers(), s.getCondensationCatalyzers(),s.getCleavageCatalyzers(), s.getCatalyzers(), s.getSpeciesAsReactar()])
    catalyzersAsSpeciesDf = setTable(pd, catalyzerAsSpeciesRows, speciesColumns)

    path = os.path.join(BASE_DIR, "io/Tabulator/output/output.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        catalystDf.to_excel(writer, index=False, startrow=2, startcol=1, sheet_name="Sheet1")
        speciesDf.to_excel(writer, index=False, startrow=len(catalystDf)+5, startcol=1, sheet_name="Sheet1")
        catalyzersAsSpeciesDf.to_excel(writer, index=False, startrow=len(catalystDf)+len(speciesDf)+8, startcol=1, sheet_name="Sheet1")

    wb = load_workbook(path)
    ws = wb.active
    titles = ["Catalysts Information", "Species Information", "Catalyzers as Species Information"]
    setTitle(ws, titles[0], startRow=2, startCol=2, endCol=len(catalystColumns)+1)
    speciesSR = len(catalystDf)+5
    setTitle(ws, titles[1], startRow=speciesSR, startCol=2, endCol=len(speciesColumns)+1)
    catalyzersAsSpeciesSR = speciesSR+len(speciesDf)+3
    setTitle(ws, titles[2], startRow=catalyzersAsSpeciesSR, startCol=2, endCol=len(speciesColumns)+1)

    white = PatternFill(start_color="ffffff", end_color="ffffff", fill_type="solid")
    lightGray = PatternFill(start_color="f0f0f0", end_color="f0f0f0", fill_type="solid")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    setTableStyle(ws, 3, catalystColumns, catalystDf, border, white, lightGray)
    setTableStyle(ws, len(catalystDf)+6, speciesColumns, speciesDf, border, white, lightGray)
    setTableStyle(ws, len(catalystDf)+len(speciesDf)+9, speciesColumns, catalyzersAsSpeciesDf, border, white, lightGray)
    resizeCells(ws,titles,catalystColumns,speciesColumns)

    wb.save(path)

def writeAnalysOnExcel(data, serieName):
    columns = ['Lap', 'Interrupted', 'All species', 'All reactions', 'Unique species', 'Unique reactions', 'Catalysts', 'RAF']
    rows = []
    for r in data:
        if not r[1] :
            r[1] = "No"
        else:
            r[1] = "Yes"
        if not r[7]:
            r[7] = "No"
        else:
            r[7] = "Yes"
        rows.append(r)

    analystDf = setTable(pd, rows, columns)

    path = os.path.join(BASE_DIR, "io", "launcher", "output", "series", serieName, "analysis.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        analystDf.to_excel(writer, index=False, startrow=2, startcol=1, sheet_name="Sheet1")

    wb = load_workbook(path)
    ws = wb.active
    setTitle(ws, "Analysis", startRow=2, startCol=2, endCol=len(columns)+1)

    white = PatternFill(start_color="ffffff", end_color="ffffff", fill_type="solid")
    lightGray = PatternFill(start_color="f0f0f0", end_color="f0f0f0", fill_type="solid")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    setTableStyle(ws, 3, columns, analystDf, border, white, lightGray)
    resizeCells(ws, ["Analysis"], columns, columns)
    wb.save(path)