from django.db.models.fields.related import OneToOneField
from visio.models import Pdv

class Referentiel:
  __unusedFields = ["id", "available", "sale", "redistributed", "redistributedEnduit"]
  __fields = Pdv._meta.get_fields()
  __pdvObjects = Pdv.objects.all()
  __typeOfFields = [field.name for field in __fields if (field.many_to_one or field.one_to_one)]
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
      lineValue = [cls.__computeRelations(fieldName, object, cls.__typeOfFields) for fieldName in fieldsName]
      values.append(lineValue)
    return values

  @classmethod
  def exportReferentiel(cls):
    return {'titles':cls.fieldsName, 'values':cls.values}

  @classmethod
  def __computeRelations(cls, fieldName:str, object, typeOfField):
    if fieldName in typeOfField:
      return getattr(getattr(object, fieldName), "name")
    return getattr(object, fieldName)

  @classmethod
  def __computeFieldsName(cls, fieldName):
    object = cls.__pdvObjects[0]
    dicoField = {field.name:field for field in cls.__fields}
    if fieldName in cls.__typeOfFields:
      relatedObject = getattr(object, fieldName)
      return type(relatedObject)._meta.verbose_name.title()
    return dicoField[fieldName].verbose_name

Referentiel.initClass()


    


    