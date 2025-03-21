from utils.utils import *

class Analyst:
    def __init__(self,parameters,debug,isKaufmannGenerator):
        self.debug=debug
        self.parameters=parameters
        self.isKaufmannGenerator = isKaufmannGenerator

    def getParameters(self):
        return self.parameters
    
    def getParameter(self,key):
        return self.parameters[key]
    
    def setParameters(self,parameters):
        self.parameters=parameters

    def getisKaufmannGenerator(self):
        return self.isKaufmannGenerator

    def countSpecies(self,lines):
        count = 0
        for i,line in enumerate(lines):
            if line.startswith("Cont"):
                line=lines[i+1]
                while not line.startswith("10.0"):
                    count += 1
                    line=lines[i+count+1]
                return count
    
    def countReactions(self,lines):
        count = 0
        trigger=False
        flag=False
        for i,line in enumerate(lines):
            if not trigger:
                if line.startswith("10.0"):
                    trigger=True
            else:
                if not flag:
                    if not line.startswith("10.0"):
                        flag = True
                        if "NESSUNA REAZIONE GENERATA" in line:
                            continue
                        else:
                            count += 1
                else:
                    count += 1
        return count
    
    def countFoodSpecies(self,lines):
        count = 0
        for line in lines:
            if line.startswith("10.0"):
                count += 1
        return count

    def countCatalysts(self,lines):
        count = 0
        catalysts = [line.split()[0] for line in lines if not lines.index(line) == 0]
        catalysts = list(set(catalysts))
        count=len(catalysts)
        return count

    def countRAFSpecies(self,lines):
        count=0
        for line in lines:
            if len(line.strip()) == 0:
                break
            count += 1
        count -= 1
        return count

    def countRAFReactions(self,lines):
        count=0
        flag=False
        for line in lines:
            if line.startswith("10.0"):
                break
            if flag:
                count += 1
            if len(line.strip()) == 0 and not flag:
                flag=True
        return count

    def countRAFFood(self,lines):
        count=0
        flag=False
        for line in lines:
            if line.startswith("10.0") and not flag:
                flag=True
            if flag:
                count += 1
        count -= 1
        return count
    
    def countRAFCatalysts(self,lines):
        count=0
        flag=False
        catalysts=[]
        for line in lines:
            if line.startswith("10.0"):
                break
            if flag:
                splitted = line.split('>')
                reactants = cleanReaction(splitted[0])
                products = cleanReaction(splitted[1])
                for reactant in reactants:
                    if reactant in products and reactant not in catalysts:
                        catalysts.append(reactant)
                        count += 1
            if len(line.strip()) == 0 and not flag:
                flag=True
        return count
    
    def countCatalystsChemistry(self,lines):
        count = 0
        catalysts=[]
        trigger=False
        flag=False
        for i,line in enumerate(lines):
            if not trigger:
                if line.startswith("10.0"):
                    trigger=True
            else:
                if not flag:
                    if not line.startswith("10.0"):
                        flag = True
                        if "NESSUNA REAZIONE GENERATA" in line:
                            continue
                        else:
                            splitted = line.split('>')
                            reactants = cleanReaction(splitted[0])
                            products = cleanReaction(splitted[1])
                            for reactant in reactants:
                                if reactant in products and reactant not in catalysts:
                                    catalysts.append(reactant)
                                    count += 1
                else:
                    splitted = line.split('>')
                    reactants = cleanReaction(splitted[0])
                    products = cleanReaction(splitted[1])
                    for reactant in reactants:
                        if reactant in products and reactant not in catalysts:
                            catalysts.append(reactant)
                            count += 1
        return count
    
    def getData(self):
        rows = []
        regexRAF = r"^Protocell\d+RAF.txt$"
        if self.debug:
            print(colored("Analizzo la serie '"+str(self.getParameter("serieName"))+"'","yellow"))
        for lap in range(0, self.getParameter("launches")):
            if self.debug:
                print(colored("Lancio "+str(lap+1),"cyan",attrs=['bold']))
            path=os.path.join("io", "launcher", "output", "series", str(self.getParameter("serieName")), str(lap+1), "output")
            files=os.listdir(path)
            for file in files:
                lines = readFile(os.path.join(path, file))
                lines=[line.strip() for line in lines if line.strip()]
                if "allReactions.txt" in file:
                    allSpecies = self.countSpecies(lines)
                    allReactions = self.countReactions(lines)
                    if self.debug:
                        print(colored("Trovate "+str(allSpecies)+" specie e "+str(allReactions)+" reazioni","light_grey"))
                if "uniqueReactions.txt" in file:
                    uniqueSpecies = self.countSpecies(lines)
                    uniqueReactions = self.countReactions(lines)
                    foodSpecies = self.countFoodSpecies(lines)
                    if self.debug:
                        print(colored("Trovate "+str(uniqueSpecies)+" specie uniche e "+str(uniqueReactions)+" reazioni uniche","light_grey"))
                    if self.getisKaufmannGenerator():
                        catalysts=self.countCatalystsChemistry(lines)
                if "outputRules.txt" in file and not self.getisKaufmannGenerator():
                    catalysts = self.countCatalysts(lines)
                    if self.debug:
                        print(colored("Trovati "+str(catalysts)+" catalizzatori","light_grey"))
            interrupted=False
            if "report.txt" in files:
                interrupted=True
            RAFfile = [f for f in files if re.match(regexRAF, f)]
            RAFspecies, RAFreactions, RAFfood, RAFcatalysts = 0, 0, 0, 0
            if RAFfile:
                lines = readFile(os.path.join(path, RAFfile[0]))
                RAFspecies=self.countRAFSpecies(lines)
                RAFreactions=self.countRAFReactions(lines)
                RAFfood=self.countRAFFood(lines)
                RAFcatalysts=self.countRAFCatalysts(lines)
                if self.debug:
                    print(colored("RAF individuato","light_grey"))
                RAF=True
            else:
                RAF=False
            if self.debug:
                if interrupted:
                    print(colored("Lancio "+str(lap+1)+" interrotto a causa dello scadere del timer","yellow"))
                print(colored("Lancio "+str(lap+1)+" analizzato","green",attrs=['bold']))
            rows.append([lap+1, interrupted, allSpecies, allReactions, uniqueSpecies, uniqueReactions, foodSpecies, catalysts, RAF, RAFspecies, RAFreactions, RAFfood, RAFcatalysts])
        return rows
    
    def writeFile(self, rows):
        try:
            writeAnalysOnExcel(rows, self.getParameter("serieName"))
        except PermissionError:
            print(f"ERRORE! Il file è già aperto in Excel. Chiudilo e riprova.")