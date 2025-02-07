from utils.utils import *

class Analyst:
    def __init__(self,parameters,debug):
        self.debug=debug
        self.parameters=parameters

    def getParameters(self):
        return self.parameters
    
    def getParameter(self,key):
        return self.parameters[key]
    
    def setParameters(self,parameters):
        self.parameters=parameters

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
        len = lines.__len__()
        for i,line in enumerate(lines):
           if line.startswith("10.0"):
                while True:
                    count += 1
                    if i+count == len:
                        return count
                    line=lines[i+count]

    def countCatalysts(self,lines):
        count = 0
        count = lines.__len__()-1
        return count
    
    def getData(self):
        rows = []
        files = ["output-allReactions.txt","output-uniqueReactions.txt","outputRules.txt"]
        if self.debug:
            print(colored("Analizzo la serie '"+str(self.getParameter("serieName"))+"'","yellow"))
        for lap in range(0, self.getParameter("launches")):
            if self.debug:
                print(colored("Lancio "+str(lap+1),"cyan",attrs=['bold']))
            path=os.path.join("io", "launcher", "output", "series", str(self.getParameter("serieName")), str(lap+1), "output")
            for file in files:
                lines = readFile(os.path.join(path, file))
                lines=[line.strip() for line in lines if line.strip()]
                if file == "output-allReactions.txt":
                    allSpecies = self.countSpecies(lines)
                    allReactions = self.countReactions(lines)
                    if self.debug:
                        print(colored("Trovate "+str(allSpecies)+" specie e "+str(allReactions)+" reazioni","light_grey"))
                if file == "output-uniqueReactions.txt":
                    uniqueSpecies = self.countSpecies(lines)
                    uniqueReactions = self.countReactions(lines)
                    if self.debug:
                        print(colored("Trovate "+str(uniqueSpecies)+" specie uniche e "+str(uniqueReactions)+" reazioni uniche","light_grey"))
                if file == "outputRules.txt":
                    catalysts = self.countCatalysts(lines)
                    if self.debug:
                        print(colored("Trovati "+str(catalysts)+" catalizzatori","light_grey"))
            interrupted=False
            if "report.txt" in os.listdir(path):
                interrupted=True
            if self.debug:
                if interrupted:
                    print(colored("Lancio "+str(lap+1)+" interrotto a causa dello scadere del timer","yellow"))
                print(colored("Lancio "+str(lap+1)+" analizzato","green",attrs=['bold']))
            rows.append([lap+1, interrupted, allSpecies, allReactions, uniqueSpecies, uniqueReactions, catalysts])
        return rows
    
    def writeFile(self, rows):
        writeAnalysOnExcel(rows, self.getParameter("serieName"))