
class Species:
    def __init__(self,name):
        self.name=name
        self.isInitial=False

    def __len__(self):
        return len(self.name)

    def setName(self,name):
        self.name=name    

    def getName(self):
        return self.name
    
    def setIsInitial(self,isInitial):
        self.isInitial=isInitial

    def getIsInitial(self):
        return self.isInitial