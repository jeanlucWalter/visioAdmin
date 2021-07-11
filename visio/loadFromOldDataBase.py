from django.db.models import fields
from termcolor import colored
import mysql.connector as database
from visio.models import Drv, Agent, Dep, Bassin, Ville

connection = database.connect(
  user = "visioOld",
  password = "65dFXO[MThGYk9sa",
  host = "localhost",
  database = "visioOld"

)
cursor = connection.cursor()
class Variables:

  def __init__(self):
    self.fieldsPdv = []
    self.dictPdv = []
    self.dictdrv = {}
    self.dictAgent = {}
    self.dictdep = {}
    self.dictbassin = {}
    self.dictville = {}
    self.typeObject = {"drv":Drv, "dep":Dep, "bassin":Bassin, "ville":Ville}

var = Variables()

def getPdv():
  try:
    query = "SHOW COLUMNS FROM ref_pdv_1"
    cursor.execute(query)
    var.fieldsPdv = [field[0] for field in cursor]
  except database.Error as e:
    print(colored("Error getPdv" + e), "red")

  try:
    query = "SELECT * FROM ref_pdv_1"
    cursor.execute(query)
    for line in cursor:
      var.dictPdv.append(line)
  except database.Error as e:
    print(colored("Error getDrv" + e), "red")

def getAgent():
  try:
    query = "SELECT id, name FROM ref_actor_1"
    cursor.execute(query)
    drvCorrespondance = getDrvCorrespondance()
    for (id, name) in cursor:
      existAgent = Agent.objects.filter(name__icontains=name)
      if not existAgent.exists():
        idDrv = drvCorrespondance[id]
        nameDrv = var.dictdrv[idDrv]
        drv = Drv.objects.filter(name=nameDrv)
        if drv.exists():
          Agent.objects.create(name=name, drv=drv.first())
        else:
          print(colored("Agent {} has no drv".format(name), "red"))
      var.dictAgent[id] = name
  except database.Error as e:
    print(colored("Error getAgent" + e, "red"))
  print("Pdv loaded")

def getDrvCorrespondance():
  IndexAgent = var.fieldsPdv.index("id_actor")
  IndexDrv =  var.fieldsPdv.index("id_drv")
  drvCorrespondance = {}
  for line in var.dictPdv:
    idAgent = line[IndexAgent]
    if not idAgent in drvCorrespondance:
      drvCorrespondance[idAgent] = line[IndexDrv]
  return drvCorrespondance

def getObject(type:str):
  try:
    query = "SELECT id, name FROM ref_{}_1".format(type)
    cursor.execute(query)
    for (id, name) in cursor:
      name = unProtect(name)
      existobject = var.typeObject[type].objects.filter(name__iexact=name)
      if not existobject.exists():
        var.typeObject[type].objects.create(name=name)
      dict = getattr(var, "dict" + type)
      dict[id] = name
  except database.Error as e:
    print(colored("Error getObject {} {}".format(type, e), "red"))
  print(type + " loaded")

def unProtect(string:str) ->str:
	protectDict = {"@":"<£arobase>", "\n":"<£newLine>", "&":"<£andCommercial>", "'":"<£quote>", "\t":"<£tab>", "\\":"<£backSlash>", "\"":"<£doubleQuote>", ".":"<£dot>", "/":"<£slash>", "?":"<£questionMark>", "`":"<£backQuote>", ";":"<£semicolon>", ",":"<£coma>"}
	for (symbol, protect) in protectDict.items():
		string = string.replace(protect, symbol)
	string = string.replace("  ", " ")
	return string.strip()

def loadData():
  print (colored('\033[1m' + "End migration, start loadData" + '\033[0m', "blue"))
  getPdv()
  for type in ["drv", "dep", "bassin", "ville"]:
    getObject(type)
  getAgent()