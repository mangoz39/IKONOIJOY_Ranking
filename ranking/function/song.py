class Song:
    def __init__(self, name, ytid, group):
        self.name = name
        self.ID = ytid
        self.group = group

    def getName(self):
        return self.name

    def getID(self):
        return self.ID

    def getGroup(self):
        return self.group

