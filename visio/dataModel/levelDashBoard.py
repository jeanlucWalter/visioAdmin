from json import dumps
from re import sub

class TreeLevel:
  def __init__(self, id:int, subLevels:list=[]):
    self.id = id
    self.subLevels = subLevels

  @property
  def toJson(self):
    if self.subLevels:
      return (self.id, [subLevel.toJson for subLevel in self.subLevels])
    return self.id

class Level:
  def __init__(self, id:int, levelName:str, listDashBoards:list, subLevel=None):
    self.id = id
    self.levelName = levelName
    self.listDashBoards = listDashBoards
    self.subLevel = subLevel

  @property
  def toJson(self):
    structure = ['id', 'levelName', 'listDashBoards', 'subLevel']
    return {"structure":structure, "levels":self.__getLevelList(), "dashBoard":self.__getDashBoardDict()}

  def __getLevelList(self):
    result = [self.id, self.levelName, [dashBoard.id for dashBoard in self.listDashBoards]]
    if self.subLevel:
      result.append(self.subLevel.__getLevelList())
    return result

  def __getDashBoardDict(self, dictDashBoards={}):
    for dashBoard in self.listDashBoards:
      if not dashBoard.id in dictDashBoards:
        dictDashBoards[dashBoard.id] = dashBoard.toJson
    if self.subLevel:
      self.subLevel.__getDashBoardDict(dictDashBoards)
    return dictDashBoards

class LevelWithTree(Level):
  def __init__(self, id:int, levelName:str, listDashBoards:list, treeLevel:TreeLevel, subLevel:Level=None):
    super().__init__(id=id, levelName=levelName, listDashBoards=listDashBoards, subLevel=subLevel)
    self.treeLevel=treeLevel

  @property
  def toJson(self):
    levelJson = super().toJson
    levelJson["tree"] = self.treeLevel.toJson
    return levelJson



class DashBoard:
  def __init__(self, id:int, name:str):
    self.id = id
    self.name = name

  @property
  def toJson(self):
    return {"name":self.name}

listDashBoards = [
  DashBoard(1, "Marché P2CD"),
  DashBoard(2, "Marché Enduit"),
  DashBoard(3, "PdM P2CD"),
  DashBoard(4, "PdM Enduit")
]

listDashBoardsNat = [
  DashBoard(5, "Synthèse P2CD"),
  DashBoard(6, "Synthèse Enduit"),
  DashBoard(7, "Suivi des ventes"),
  DashBoard(8, "Suivi de l'AD")
]

listDashBoardsAgent = [
  DashBoard(9, "Agent P2CD"),
  DashBoard(10, "Agent Enduit")
]
subTreeLevel2 = {id:None for id in range(2, 8)}
for id in [3, 1, 2, 4, 5, 6]:
  subTreeLevel2[id] = [TreeLevel(id= 1 + idSub + (id - 1) * 6, subLevels=[]) for idSub in range(6)]
subTreeLevels = [TreeLevel(id=id, subLevels=subTreeLevel2[id]) for id in [3, 1, 2, 4, 5, 6]]
treeLevel = TreeLevel(id="root", subLevels=subTreeLevels)

nationalLevel = LevelWithTree(id=1, levelName="root", listDashBoards=listDashBoards+listDashBoardsNat, treeLevel=treeLevel)
drvLevel = Level(id=2, levelName="drv", listDashBoards=listDashBoards)
nationalLevel.subLevel = drvLevel
sectorLevel = Level(id=3, levelName="agent", listDashBoards=listDashBoards+listDashBoardsAgent)
drvLevel.subLevel = sectorLevel

result = nationalLevel.toJson
result["drv"] = {
    1: "SUD-OUEST",
    2: "RHONE ALPES",
    3: "ILE DE France",
    4: "SUD-EST",
    5: "OUEST",
    6: "NORD-EST"
  }

result["agent"] = {
  1: "CASCALES LAURENT",
  2: "RIBIERE FRANCK",
  3: "BRAY JEROME",
  4: "TEIXEIRA SANDRINE",
  5: "TERKI KARIM",
  6: "BARGOZZA FLORENT",
  7: "BIDARD OLIVIER",
  8: "FRESNEAU ALEXANDRE",
  9: "VAILLANT SEBASTIEN",
  10: "COTTERLAZ-RANNARD A.",
  11: "LYS JEROME",
  12: "PONCE MICHAEL",
  13: "ROBIEUX CHARLY",
  14: "BOUMARAF CHRISTOPHE",
  15: "FREITAS FILIPE",
  16: "JAILLAT FREDERIC",
  17: "PALTANI REGIS",
  18: "HENRY MATHIEU",
  19: "DIMULLE ALAIN",
  20: "GOUESSAN GUILLAUME",
  21: "DAUTHUILLE STEPHANE",
  22: "DO FETAL PASCAL",
  23: "BIERE GERALDINE",
  24: "BRUNET CHRISTOPHE",
  25: "LEVESQUE LILIAN",
  26: "BARTOLO DIDIER",
  27: "MARCHAL TONY",
  28: "CARUCCIO STEPHANE",
  29: "AUBINEAU NICOLAS",
  30: "DELALANDE JEROME",
  31: "BATOT KEVIN",
  32: "FISCHER ALEXANDRE",
  33: "FORTIN ANNE",
  34: "CHAMBEFORT PATRICE",
  35: "GARRAUT ROLAND",
  36: "DANJOU SEVERINE",
  37: "LAURENT FREDERIC",
  38: "ROUX PHILIPPE",
  39: "ANTUNES JEAN-MANUEL",
  40: "CHARVOT THOMAS",
  41: "BOULET MORGANE",
  42: "DIMULLE",
  43: "RIBIERE",
  44: "GOFFIN",
  45: "BARTOLO",
  46: "GUERIN",
  47: "ROUX",
  48: "GARRAUT"
}

print(dumps(result))
with open("level.json", "w") as jsonFile:
    jsonFile.write(dumps(result))
