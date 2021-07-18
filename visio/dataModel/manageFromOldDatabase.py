from os import name
from dateutil import tz
from datetime import datetime
import mysql.connector as db
import copy
# from django.db.models import fields
from visio.models import Pdv, Drv, Agent, Dep, Bassin, Ville, AgentFinitions, SegmentCommercial, SegmentMarketing, Enseigne, Ensemble, SousEnsemble, Site

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
  dictHolding = {}
  typeObject = {
    "pdv":Pdv, "agent":Agent, "agentfinitions":AgentFinitions, "dep":Dep, "drv":Drv, "bassin":Bassin, "ville":Ville, "segCo":SegmentCommercial,
    "segment":SegmentMarketing, "unused1":Site, "unused2":SousEnsemble, "unused3":Ensemble, "holding":Enseigne
    }
  connection = None
  cursor = None
  

  def emptyDatabase(self, start:bool) -> dict:
    if start:
      self.connectionNew = db.connect(
        user = "visio.4.0",
        password = 'aFH4l)Ux1Xo6Rws4',
        host = "localhost",
        database = "visio.4.0"
      )
      self.cursorNew = self.connectionNew.cursor()
      self.typeObjectList = list(self.typeObject.values())

    if self.typeObjectList:
      model = self.typeObjectList.pop(0)
      model.objects.all().delete()
      table = model.objects.model._meta.db_table
      self.cursorNew.execute("ALTER TABLE {} AUTO_INCREMENT=1;".format(table))
      return {'query':'emptyDatabase', 'message':"la table {} a été vidée.".format(table), 'end':False, 'errors':[]}
    self.connectionNew.close()
    return {'query':'emptyDatabase', 'message':"<b>La base de données a été vidée</b>", 'end':True, 'errors':[]}


  def populateDatabase(self, start:bool, method:str) -> 'list(str)':
    if start:
      ManageFromOldDatabase.connection = db.connect(
      user = "visioOld",
      password = "65dFXO[MThGYk9sa",
      host = "localhost",
      database = "visioOld"
      )
      ManageFromOldDatabase.cursor = ManageFromOldDatabase.connection.cursor()
      self.dictPopulate = [
        ("PdvOld",[]), ("Object", ["drv"]), ("Agent", []), ("Object", ["dep"]), ("Object", ["bassin"]), ("Object", ["holding"]), ("Ensemble", []),
        ("ObjectFromPdv", ["sous-ensemble", SousEnsemble]), ("ObjectFromPdv", ["site", Site]),
        ("Object", ["ville"]), ("Object", ["segCo"]), ("Object", ["segment"]), ("AgentFinitions", []), ("PdvNew", [])]
    if self.dictPopulate:
      tableName, variable = self.dictPopulate.pop(0)
      table, error = getattr(self, "get" + tableName)(*variable)
      error = [error] if error else []
      message = "L'ancienne base de données est lue" if tableName == "PdvOld" else "La table {} est remplie ".format(str(table))
      return {'query':method, 'message':message, 'end':False, 'errors':error}
    ManageFromOldDatabase.connection.close()
    return {'query':method, 'message':"<b>La base de données a été remplie</b>", 'end':True, 'errors':[]}

  def getPdvOld(self):
    if not self.listPdv:
      try:
        query = "SHOW COLUMNS FROM ref_pdv_1"
        ManageFromOldDatabase.cursor.execute(query)
        self.fieldsPdv = [field[0] for field in ManageFromOldDatabase.cursor]
      except db.Error as e:
        return (False, "getPdvOld for fields " + repr(e))

      try:
        query = "SELECT * FROM ref_pdv_1 WHERE `Closed_by_OM` <> 'y'"
        ManageFromOldDatabase.cursor.execute(query)
        for line in ManageFromOldDatabase.cursor:
          line = [self.unProtect(item) for item in line]
          self.listPdv.append(line)
      except db.Error as e:
        return (False, "getPdvOld for values " + repr(e))
    return (False, False)

  def getPdvNew(self):
    for line in self.listPdv:
      keyValues = {}
      keyValues["drv"] = self.__findObject("id_drv", self.dictDrv, line, Drv)
      keyValues["agent"] = self.__findObject("id_actor", self.dictAgent, line, Agent)
      keyValues["dep"] = self.__findObject("id_dep", self.dictDep, line, Dep)
      keyValues["bassin"] = self.__findObject("id_bassin", self.dictBassin, line, Bassin)
      keyValues["ville"] = self.__findObject("id_ville", self.dictVille, line, Ville)
      ensemble = Ensemble.objects.filter(name__iexact=line[self.fieldsPdv.index("ensemble")]).first()
      keyValues["enseigne"] = ensemble.enseigne
      keyValues["ensemble"] = ensemble
      keyValues["sous_ensemble"] = SousEnsemble.objects.filter(name__iexact=line[self.fieldsPdv.index("sous-ensemble")]).first()
      keyValues["segment_commercial"] = self.__findObject("id_segCo", self.dictSegco, line, SegmentCommercial)
      keyValues["segment_marketing"] = self.__findObject("id_segment", self.dictSegment, line, SegmentMarketing)
      keyValues["code"] = line[self.fieldsPdv.index("PDV code")] if line[self.fieldsPdv.index("PDV code")] else None
      keyValues["name"] = line[self.fieldsPdv.index("PDV")] if line[self.fieldsPdv.index("PDV")] else None
      keyValues["latitude"] = line[self.fieldsPdv.index("latitude")] if line[self.fieldsPdv.index("PDV code")] else None
      keyValues["longitude"] = line[self.fieldsPdv.index("longitude")] if line[self.fieldsPdv.index("PDV")] else None
      keyValues["available"] = self.__computeBoolean(line, field="does_not_exist", valueIfNotExist="y")
      keyValues["sale"] = self.__computeBoolean(line, field="sale", valueIfNotExist="y")
      keyValues["redistributed"] = self.__computeBoolean(line, field="redistributed", valueIfNotExist="y")
      keyValues["redistributedEnduit"] = self.__computeBoolean(line, field="redistributedEnduit", valueIfNotExist="y")
      keyValues["pointFeu"] = self.__computeBoolean(line, field="does_not_exist", valueIfNotExist="N")
      keyValues["closedAt"] = self.__computeClosedAt(line)

      for field, object in keyValues.items():
        if object == None and field != "closedAt":
          return [False, "field {}, Pdv {}, code {} does not exists".format(field, keyValues["name"], keyValues["code"])]
      existsPdv = Pdv.objects.filter(code=keyValues["code"])
      if not existsPdv.exists():
        Pdv.objects.create(**keyValues)
      else:
        return (False, "Pdv {}, code {} already exists".format(keyValues["name"], keyValues["code"]))
    return ("Pdv", False)

  def __computeBoolean(self, line:list, field:str, valueIfNotExist:str) -> bool:
    valueFound = line[self.fieldsPdv.index(field)]
    return valueFound != valueIfNotExist

  def __computeClosedAt(self, line:list):
    timestamp = line[self.fieldsPdv.index("toBeClosed")]
    if timestamp:
      return datetime.fromtimestamp(timestamp, tz=tz.gettz("Europe/Paris"))
    return None

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

  def getEnsemble(self):
    IndexEnsemble = self.fieldsPdv.index("ensemble")
    IndexEnseigne = self.fieldsPdv.index("id_holding")
    dicoEnsemble, dicoEnseigne = {}, {}
    for line in self.listPdv:
      nameEnsemble = line[IndexEnsemble]
      idEnseigneOld = self.__cleanEnseigne(line[IndexEnseigne], nameEnsemble)
      nameEnseigne = self.dictHolding[idEnseigneOld]
      if not nameEnseigne in dicoEnsemble:
        dicoEnsemble[nameEnseigne] = []
      if not nameEnsemble in dicoEnsemble[nameEnseigne]:
        dicoEnsemble[nameEnseigne].append(nameEnsemble)
        if not nameEnseigne in dicoEnseigne:
          existsObject = Enseigne.objects.filter(name__iexact=nameEnseigne)
          if existsObject.exists:
            dicoEnseigne[nameEnseigne] = existsObject.first()
          else:
            return (False, "Error getEnsemble : Enseigne {} does not exist".format(nameEnseigne))
        Ensemble.objects.create(name=nameEnsemble, enseigne=dicoEnseigne[nameEnseigne])
    return ("Ensemble", False)

  def __cleanEnseigne(self, idEnseigne:int, nameEnsemble:str) ->str:
    if nameEnsemble == "BIGMAT FRANCE": return 1 #CMEM
    if nameEnsemble == "PROSPECTS AD CMEM": return 1
    if "POINT P " in nameEnsemble: return 2 #SGBD France
    if "CHAUSSON MATERIAUX" in nameEnsemble: return 11 #Chausson
    if "GEDIMAT" in nameEnsemble: return 3 #Gédimat
    if "EX-" in nameEnsemble: return 9 # Nég ancien PdV
    elif nameEnsemble == "DMBP": return 2 # SGBD France
    elif nameEnsemble == "PROSPECTS SGBD FRANCE": return 2  #SGBD France
    elif nameEnsemble == "RÉSEAU PRO GRAND OUEST": return 13 # Bois et matériaux
    elif nameEnsemble == "RÉSEAU PRO IDF NORD EST": return 13 # Bois et matériaux
    elif nameEnsemble == "LITT DIFFUSION": return 5 # Sig France
    elif nameEnsemble == "PANOFRANCE": return 5 # Sig France
    elif nameEnsemble == "CIFFREO BONA": return 4 # Groupement régionaux
    elif nameEnsemble == "UNION MATERIAUX GROUPE": return 10 #Altéral
    elif nameEnsemble == "PROSPECTS AD EX NEGOCE": return 9 # Nég ancien PdV
    elif nameEnsemble == "GROUPE SAMSE": return 7 # MCD
    return idEnseigne

  def getObjectFromPdv(self, field, classObject):
    IndexSousEnsemble = self.fieldsPdv.index(field)
    dicoSousEnsemble = ['Not assigned']
    classObject.objects.create(name='Not assigned')
    for line in self.listPdv:
      nameSousEnsemble = line[IndexSousEnsemble]
      if not nameSousEnsemble in dicoSousEnsemble:
        dicoSousEnsemble.append(nameSousEnsemble)
        classObject.objects.create(name=nameSousEnsemble)
    return (classObject.__name__, False)

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

manageFromOldDatabase = ManageFromOldDatabase() 