
import enum
import re

class TableModel:

  def __init__(self, model, objects:list, unsuedField:list=[], interpretBoolean:dict={}, interpretRegX:dict={}):
    self.model = model
    self.__fields = model._meta.fields
    self.__objects = objects
    self.__foreignKeyFields = [field.name for field in self.__fields if (field.many_to_one or field.one_to_one)]
    self.__unusedFields = unsuedField
    self.__interpretBoolean = interpretBoolean
    self.__interpretRegeX = interpretRegX
    self.fieldsName:list = self._computeFieldsName()
    self.values:dict = self._computeValues()

  @property
  def json(self):
    return {'titles':self.fieldsName, 'values':list(self.values.values()), 'tableIndex':list(self.values.keys())}

  def _computeValues(self, idPdv:bool = False):
    fieldsName = [field.name for field in self.__fields if not field.name in self.__unusedFields]
    values = {}
    for object in self.__objects:
      id = object.id
      lineValue = [self.__computeRelations(fieldName, object, idPdv) for fieldName in fieldsName]
      values[id] = lineValue
    return values

  def __computeRelations(self, fieldName:str, object, idPdv:bool):
    if fieldName in self.__foreignKeyFields:
      value = getattr(object, fieldName).id if (fieldName == "pdv" and idPdv) else getattr(object, fieldName).name
    else:
      value = getattr(object, fieldName)
    if fieldName in self.__interpretBoolean:
      return self.__interpretBoolean[fieldName][1] if value else self.__interpretBoolean[fieldName][0]
    elif fieldName in self.__interpretRegeX:
      return re.search(self.__interpretRegeX[fieldName], str(value)).group(1) if value else ""
    return value

  def _computeFieldsName(self):
    return [self.__computeFieldsName(field.name) for field in self.__fields if not field.name in self.__unusedFields]
  
  def __computeFieldsName(self, fieldName):
    object = self.__objects[0]
    dicoField = {field.name:field for field in self.__fields}
    if fieldName in self.__foreignKeyFields:
      relatedObject = getattr(object, fieldName)
      return type(relatedObject)._meta.verbose_name.title()
    return dicoField[fieldName].verbose_name

class TableVentes(TableModel):
  def __init__(self, model, objects:list, pdvFields:list, volFields:list, sumLast3:str, unsuedField:list=[], interpretBoolean:dict={}, interpretRegX:dict={}):
    self.__pdvFields = pdvFields
    self.__volFields = volFields
    self.__sumLast3 = sumLast3
    super().__init__(model, objects, unsuedField, interpretBoolean, interpretRegX)


  def _computeFieldsName(self):
    return self.__pdvFields + self.__volFields 

  def _computeValues(self):
    values = super()._computeValues(idPdv=True)
    fieldsPdv = tablePdv.json['titles']
    valuesPdv = tablePdv.json['values']
    dictResult = {}
    for lineVentes in values.values():
      self.__computeLines(dictResult, lineVentes, valuesPdv, fieldsPdv)

    self.__formatNumbers(dictResult)
    return dictResult

  def __computeLines(self, dictResult, lineVentes, valuesPdv, fieldsPdv):
    idPdv = lineVentes[0]
    if idPdv in dictResult:
      newLineVentes = dictResult[idPdv]
    else:
      newLineVentes = [0.0] * len(self.fieldsName)
      dictResult[idPdv] = newLineVentes
      linePdv = valuesPdv[idPdv]
      for index, field in enumerate(self.__pdvFields):
        indexFieldPdv = fieldsPdv.index(field)
        newLineVentes[index] = linePdv[indexFieldPdv]

    field = f"{lineVentes[1]} {lineVentes[2]}"
    if field in self.fieldsName:
      index = self.fieldsName.index(field)
      newLineVentes[index] = lineVentes[3]

  def __formatNumbers(self, dictResult):
    sumLast3Index = self.fieldsName.index(self.__sumLast3)
    for line in dictResult.values():
      line[sumLast3Index] = sum(line[sumLast3Index - 3:sumLast3Index])
      for index, value in enumerate(line):
        if type(value) == float:
          line[index] =  "" if value == 0 else f"{value:11,.2f}".replace(",", " ").replace(".", ",")

# LOAD STRUCTURE
from visio.models import Pdv, Ventes, Industrie

if len(Pdv.objects.all()) != 0:
  tablePdv = TableModel(
    model = Pdv,
    objects = Pdv.objects.all(),
    unsuedField = ["id", "available", "sale", "redistributed", "redistributedEnduit"],
    interpretBoolean = {"pointFeu":("", "Point Feu")},
    interpretRegX = {"closedAt":r'^(\d{4}-\d{2}-\d{2}).*'}
  )
else:
  tablePdv = None

siniatProductsId = [Industrie.objects.filter(name=name)[0].id for name in ["Siniat", "Pregy", "Salsi"]]
objects = []
for id in siniatProductsId:
  objects += Ventes.objects.filter(industry=id)

if len(Ventes.objects.all()) != 0 and len(Pdv.objects.all()) != 0:
  tableVentes = TableVentes(
    model = Ventes,
    objects = objects,
    pdvFields = ["PDV code", "PDV", "Drv", "Agent", "Département"],
    volFields = ["Siniat plaque", "Siniat cloison", "Siniat doublage", "Siniat P2CD", "Pregy enduit", "Pregy mortier", "Salsi enduit", "Salsi mortier"],
    sumLast3 = "Siniat P2CD",
    unsuedField = ["id", "date"],
  )
else:
  tableVentes = None










