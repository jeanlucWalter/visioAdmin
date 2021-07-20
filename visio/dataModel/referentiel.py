from django.db.models.fields.related import OneToOneField
from visio.models import Pdv
import re

class Referentiel:
  __unusedFields = ["id", "available", "sale", "redistributed", "redistributedEnduit"]
  __fields = Pdv._meta.fields
  __pdvObjects = Pdv.objects.all()
  __foreignKeyFields = [field.name for field in __fields if (field.many_to_one or field.one_to_one)]
  __interpretBoolean = {"pointFeu":("", "Point Feu")}
  __interpretRegeX = {"closedAt":r'^(\d{4}-\d{2}-\d{2}).*'}
  fieldName = None
  values = None

  @classmethod
  def initClass(cls):
    cls.fieldsName = [cls.__computeFieldsName(field.name) for field in cls.__fields if not field.name in cls.__unusedFields]
    cls.values = cls.__computeValues()

  @classmethod
  def __computeValues(cls):
    fieldsName = [field.name for field in cls.__fields if not field.name in cls.__unusedFields]
    values = []
    for object in cls.__pdvObjects:
      lineValue = [cls.__computeRelations(fieldName, object) for fieldName in fieldsName]
      values.append(lineValue)
    return values

  @classmethod
  def exportReferentiel(cls):
    return {'titles':cls.fieldsName, 'values':cls.values}

  @classmethod
  def __computeRelations(cls, fieldName:str, object):
    if fieldName in cls.__foreignKeyFields:
      value = getattr(object, fieldName).name
    else:
      value = getattr(object, fieldName)
    if fieldName in cls.__interpretBoolean:
      return cls.__interpretBoolean[fieldName][1] if value else cls.__interpretBoolean[fieldName][0]
    elif fieldName in cls.__interpretRegeX:
      return re.search(cls.__interpretRegeX[fieldName], str(value)).group(1) if value else ""
    return value
  
  @classmethod
  def __computeFieldsName(cls, fieldName):
    object = cls.__pdvObjects[0]
    dicoField = {field.name:field for field in cls.__fields}
    if fieldName in cls.__foreignKeyFields:
      relatedObject = getattr(object, fieldName)
      return type(relatedObject)._meta.verbose_name.title()
    return dicoField[fieldName].verbose_name

# if len(Pdv.objects.all()) != 0:
#   Referentiel.initClass()


    


    