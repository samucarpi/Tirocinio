
class Rule:

    def __init__(self, catalyst, type, activeSite, position, reactionClass):
        self.catalyst = catalyst
        self.type = type
        self.activeSite = activeSite
        self.position = position
        self.reactionClass = reactionClass
    
    def setCatalyst(self, catalyst):
        self.catalyst = catalyst

    def getCatalyst(self):
        return self.catalyst

    def setType(self, type):
        self.type = type

    def getType(self):
        return self.type

    def setActiveSite(self, activeSite):
        self.activeSite = activeSite
    
    def getActiveSite(self):
        return self.activeSite

    def setPosition(self, position):
        self.position = position
    
    def getPosition(self):
        return self.position
    
    def setReactionClass(self, reactionClass):
        self.reactionClass = reactionClass

    def getReactionClass(self):
        return self.reactionClass
    
    def __str__(self):
        return self.getCatalyst() + ' ' + self.getType() + ' ' + self.getActiveSite() + ' ' + self.getPosition() + ' ' + self.getReactionClass()