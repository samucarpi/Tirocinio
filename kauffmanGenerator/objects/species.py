
class Species:
    def __init__(self,name):
        self.name=name

    def __len__(self):
        return len(self.name)

    def setName(self,name):
        self.name=name    

    def getName(self):
        return self.name