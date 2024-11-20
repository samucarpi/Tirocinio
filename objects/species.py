
class Species:
    def __init__(self,name,isInitial):
        self.name=name
        self.isInitial=isInitial

    def setName(self,name):
        self.name=name    

    def getName(self):
        return self.name
    
    def setIsInitial(self,isInitial):
        self.isInitial=isInitial

    def getIsInitial(self):
        return self.isInitial