from codecs import backslashreplace_errors
from re import M
import mysql.connector as db
from django.db.models import fields
from visio.models import Pdv, Drv, Agent, Dep, Bassin, Ville, AgentFinitions, SegmentCommercial, SegmentMarketing

class ManageFromOldDatabase:
  fieldsPdv = []
  listPdv = []
  dictDrv = {}
  dictAgent = {}
  dictAgentFinitions = {}
  dictDep = {}
  dictBassin = {}
  dictVille = {}
  dictSegco = {}
  dictSegment = {}
  typeObject = {"pdv":Pdv, "agent":Agent, "agentfinitions":AgentFinitions, "dep":Dep, "drv":Drv, "bassin":Bassin, "ville":Ville, "segCo":SegmentCommercial, "segment":SegmentMarketing}
  connection = None
  cursor = None


  def distroySelf(self):
    ManageFromOldDatabase.connection.close()
    
  def distroyDatabase(self) -> str:
    ManageFromOldDatabase.connection = db.connect(
      user = "visioOld",
      password = "65dFXO[MThGYk9sa",
      host = "localhost",
      database = "visioOld"
    )
    ManageFromOldDatabase.cursor = ManageFromOldDatabase.connection.cursor()

    messages = []
    for _, Model in self.typeObject.items():
      Model.objects.all().delete()
      messages.append("la table {} a été vidée.".format(Model.objects.model._meta.db_table))
    return messages + ["La base de données a été vidée"]

  def populateDatabase(self) -> 'list(str)':
    messages = self.distroyDatabase()
    for table, variable in [("PdvOld",[]), ("Object", ["drv"]), ("Agent", []), ("Object", ["dep"]), ("Object", ["bassin"]), ("Object", ["ville"]), ("Object", ["segCo"]), ("Object", ["segment"]), ("AgentFinitions", []), ("PdvNew", [])]:
      table, error = getattr(self, "get" + table)(*variable)
      if error:
        return [error]
      if table:
        messages.append("La table {} est remplie ".format(table))
    return messages

  def getPdvOld(self):
    try:
      query = "SHOW COLUMNS FROM ref_pdv_1"
      ManageFromOldDatabase.cursor.execute(query)
      self.fieldsPdv = [field[0] for field in ManageFromOldDatabase.cursor]
    except db.Error as e:
      return (False, "Error getPdv for fields " + repr(e))

    try:
      query = "SELECT * FROM ref_pdv_1"
      ManageFromOldDatabase.cursor.execute(query)
      for line in ManageFromOldDatabase.cursor:
        line = [self.unProtect(item) for item in line]
        self.listPdv.append(line)
    except db.Error as e:
      return (False, "Error getPdv for values " + repr(e))
    return (False, False)

  def getPdvNew(self):
    print(self.fieldsPdv)
    for line in self.listPdv:
      closed = line[self.fieldsPdv.index("Closed_by_OM")]
      if closed != "y":
        keyValues = {}
        keyValues["drv"] = self.__findObject("id_drv", self.dictDrv, line, Drv)
        keyValues["agent"] = self.__findObject("id_actor", self.dictAgent, line, Agent)
        keyValues["dep"] = self.__findObject("id_dep", self.dictDep, line, Dep)
        keyValues["bassin"] = self.__findObject("id_bassin", self.dictBassin, line, Bassin)
        keyValues["ville"] = self.__findObject("id_ville", self.dictVille, line, Ville)
        keyValues["segment_commercial"] = self.__findObject("id_segCo", self.dictSegco, line, SegmentCommercial)
        keyValues["segment_marketing"] = self.__findObject("id_segment", self.dictSegment, line, SegmentMarketing)
        keyValues["code"] = line[self.fieldsPdv.index("PDV code")] if line[self.fieldsPdv.index("PDV code")] else None
        keyValues["name"] = line[self.fieldsPdv.index("PDV")] if line[self.fieldsPdv.index("PDV")] else None

        for field, object in keyValues.items():
          if object == None:
            return [False, "Error, field {}, Pdv {}, code {} does not exists".format(field, keyValues["name"], keyValues["code"])]
        existsPdv = Pdv.objects.filter(code=keyValues["code"])
        if not existsPdv.exists():
          Pdv.objects.create(**keyValues)
        else:
          return (False, "Erros, Pdv {}, code {} already exists".format(keyValues["name"], keyValues["code"]))
    return ("Pdv", False)

  def __findObject(self, fieldName, dico, line, model):
    indexObject =  self.fieldsPdv.index(fieldName)
    idObject = line[indexObject]
    nameObject =dico[idObject] if idObject in dico else dico[1]
    objectFound = model.objects.filter(name=nameObject)
    return objectFound.first() if objectFound.exists() else None

  def getAgent(self):
    try:
      query = "SELECT id, name FROM ref_actor_1"
      ManageFromOldDatabase.cursor.execute(query)
      drvCorrespondance = self.__getDrvCorrespondance()
      for (id, name) in ManageFromOldDatabase.cursor:
        existAgent = Agent.objects.filter(name__iexact=name)
        if not existAgent.exists():
          idDrv = drvCorrespondance[id]
          nameDrv = self.dictDrv[idDrv]
          drv = Drv.objects.filter(name=nameDrv)
          if drv.exists():
            Agent.objects.create(name=name, drv=drv.first())
          else:
            return (False, "Agent {} has no drv".format(name))
        self.dictAgent[id] = name
    except db.Error as e:
      return "Error getAgent" + repr(e)
    return ("Agent", False)

  def getAgentFinitions(self):
    try:
      query = "SELECT id, name, id_drv FROM ref_finition_1"
      ManageFromOldDatabase.cursor.execute(query)
      for (id, name, id_drv) in ManageFromOldDatabase.cursor:
        existsAgent = AgentFinitions.objects.filter(name__iexact=name)
        if not existsAgent.exists():
          nameDrv = self.dictDrv[id_drv]
          drv = Drv.objects.filter(name=nameDrv)
          if drv.exists():
            Agent.objects.create(name=name, drv=drv.first())
          else:
            return (False, "AgentFinitions {} has no drv".format(name))
        self.dictAgentFinitions[id] = name
    except db.Error as e:
      return "Error getAgentFinitions" + repr(e)
    return ("AgentFinitions", False)

  def __getDrvCorrespondance(self):
    IndexAgent = self.fieldsPdv.index("id_actor")
    IndexDrv =  self.fieldsPdv.index("id_drv")
    drvCorrespondance = {}
    for line in self.listPdv:
      idAgent = line[IndexAgent]
      if not idAgent in drvCorrespondance:
        drvCorrespondance[idAgent] = line[IndexDrv]
    return drvCorrespondance

  def getObject(self, type:str):
    try:
      query = "SELECT id, name FROM ref_{}_1".format(type)
      ManageFromOldDatabase.cursor.execute(query)
      for (id, name) in ManageFromOldDatabase.cursor:
        name = self.unProtect(name)
        existobject = self.typeObject[type].objects.filter(name__iexact=name)
        if not existobject.exists():
          self.typeObject[type].objects.create(name=name)
        dict = getattr(self, "dict" + type.capitalize())
        dict[id] = name
    except db.Error as e:
      return (False, "Error getObject {} {}".format(type, repr(e)))
    return (type, False)

  def unProtect(self, string):
    if type(string) == str:
      protectDict = {"@":"<£arobase>", "\n":"<£newLine>", "&":"<£andCommercial>", "'":"<£quote>", "\t":"<£tab>", "\\":"<£backSlash>", "\"":"<£doubleQuote>", ".":"<£dot>", "/":"<£slash>", "?":"<£questionMark>", "`":"<£backQuote>", ";":"<£semicolon>", ",":"<£coma>"}
      for (symbol, protect) in protectDict.items():
        string = string.replace(protect, symbol)
      string = string.replace("  ", " ")
      return string.strip()
    return string