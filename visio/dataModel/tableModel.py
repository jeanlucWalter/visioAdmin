
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
    self.fieldsName = self._computeFieldsName()
    self.values = self._computeValues()

  @property
  def json(self):
    return {'titles':self.fieldsName, 'values':self.values}

  def _computeValues(self):
    fieldsName = [field.name for field in self.__fields if not field.name in self.__unusedFields]
    values = []
    for object in self.__objects:
      lineValue = [self.__computeRelations(fieldName, object) for fieldName in fieldsName]
      values.append(lineValue)
    return values

  def __computeRelations(self, fieldName:str, object):
    if fieldName in self.__foreignKeyFields:
      value = getattr(object, fieldName).name
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

class TableVentes(TableModel):
  def _computeFieldsName(self):
    return ["PDV", "DRV", "Agent", "Siniat Plaque", "Siniat Cloison", "Siniat Doublage", "Siniat P2CD", "Pregy Enduit", "Pregy Mortier", "Salsi Enduit", "Salsi Morter"]

  def _computeValues(self):
    return [["Point P", "Sud-Ouest", "Laurent Cascales", "1000", "2000", "3000", "6000", "10", "20", "15", "25"]]

siniatProductsId = [Industrie.objects.filter(name=name)[0].id for name in ["Siniat", "Pregy", "Salsi"]]
objects = []
for id in siniatProductsId:
  objects += Ventes.objects.filter(industry=id)

if len(Ventes.objects.all()) != 0:
  tableVentes = TableVentes(
  model = Ventes,
  objects = objects,
  unsuedField = ["id", "date"]
  )
else:
  tableVentes = None










