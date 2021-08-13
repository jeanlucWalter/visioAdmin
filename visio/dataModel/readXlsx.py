from django import db
from openpyxl import load_workbook
from pathlib import Path
from unidecode import unidecode

class ReadXlsx:
  path = "visio/dataValues/xlsx/"
  __sheetName = "ReferentielVisio"
  __keyField = "Code SAP initial"
  __dicoFields = {
    "Code SAP Final": "PDV code",
    "Nom SAP": "PDV",
    "Libellé DRV SAP": "Drv",
    "Libellé Agent SAP": "Agent",
    "Dpt SAP" : "Département",
    "Libellé Bassin":"Bassin",
    "Ville SAP": "Ville",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "Segmentation Portefeuille": "Segment Commercial",
    "Libellé Typologie SAP": "Segment Marketing",
    "Nom niveau 1": "Enseigne",
    "Nom niveau 2": "Ensemble",
    "Nom niveau 3": "Sous_Ensemble",
    "Nom niveau 4": "Site",
    "Point Feu": "Point Feu",
    # "Nb visites F"
    }

  def __init__(self, fileName, tablePdv):
    self.__tableIndex = tablePdv.json["tableIndex"]
    self.__dbValues = tablePdv.json['values']
    self.__titles = ["status"] + tablePdv.json['titles']
    self.__columnKey = None
    self.__columnField = {}
    self.__errors = []
    self.__dictValues = {}
    self.__isModified = False
    pathFile = Path.cwd() / f"{self.path}{fileName}.xlsx"
    if pathFile.exists():
        xlsxworkbook = load_workbook(pathFile, data_only=True)
        try:
          self.__sheet = xlsxworkbook[self.__sheetName]
        except:
          self.__errors.append(f"L'onglet {self.__sheetName} n'existe pas.")
        else:
          self.__readFields()
          self.__writeValues()
    else:
      self.__errors.append(f"Le fichier {fileName}.xlsx n'existe pas")

  @property
  def errors(self):
    return self.__errors

  @property
  def listValues(self) -> list:
    dictXlsx = dict(self.__dictValues)
    lastIndex = len(self.__dbValues[0]) - 1
    existingPdV = [self.__buildLine(dbaseLine[0], dictXlsx, dbaseLine, lastIndex) for dbaseLine in self.__dbValues]
    newPdv = [self.__lineBold(line) for line in dictXlsx.values()]
    return existingPdV + newPdv

  @property
  def json(self)->dict:
    return {'titles':self.__titles, 'values': self.listValues, 'tableIndex':self.__tableIndex}

  def __lineBold(self, line):
    return ['Nouveau'] + [f'<b>{value}</b>' for value in line] + ['<b>Nouvelle valeur</b>']

  def __buildLine(self, code:str, dictXlsx:dict, dbaseLine:list, lastIndex:int):
    if dbaseLine[lastIndex]:
      return ['Réouverture'] + self.__createNewValues(dictXlsx.pop(code), dbaseLine) + [dbaseLine[lastIndex]]
    if code in dictXlsx:
      newValues = self.__createNewValues(dictXlsx.pop(code), dbaseLine)
      status = 'Modifié' if self.__isModified else 'Normal'
      return [status] + newValues + ['']
    else:
      lastValue = dbaseLine[lastIndex] if dbaseLine[lastIndex] else 'Pdv fermé'
      return ['Fermeture'] + [f'<i>{val}</i>' for index, val in enumerate(dbaseLine) if index != lastIndex] + [f'<i>{lastValue}</i>']


  def __readFields(self):
    column, dictField = 1, {}
    value = self.__sheet.cell(row=1, column=column).value
    while value:
      if value == self.__keyField:
        self.__columnKey = column
      elif value in self.__dicoFields:
        dictField[value] = column
      column += 1
      value = self.__sheet.cell(row=1, column=column).value
    self.__columnField = [dictField[field] for field in self.__dicoFields.keys()]

  def __writeValues (self):
    row = 2
    while True:
      key = self.__sheet.cell(row=row, column=self.__columnKey).value
      if key:
        line = [self.__sheet.cell(row=row, column=column).value for column in self.__columnField]
        self.__dictValues[str(key)] = [value if value else "" for value in line]
        row += 1
      else:
        break

  def __createNewValues (self, codeLine, dbaseLine) -> list:
    self.__isModified = False
    return [self.__computeNewValue(codeItem, dbaseLine[index], index) for index, codeItem in enumerate(codeLine)]

  def __computeNewValue(self, codeItem, dbaseItem, index):
    if self.__computeNewValueTest(codeItem, dbaseItem, index):
      return dbaseItem
    self.__isModified = True
    return f"<i>{dbaseItem}</i> <b>{codeItem}</b>"

  def __computeNewValueTest(self, codeItem, dbaseItem, index):
    if codeItem == dbaseItem if type(codeItem) == type(dbaseItem) else str(codeItem) == str(dbaseItem):
      return True
    field = self.__titles[index + 1].strip()
    if field in ["Latitude", "Longitude"]:
      if type(dbaseItem) != float or type(codeItem) != float:
        return False
      return abs(float(codeItem) - float(dbaseItem)) < 0.0002
    elif field == "Enseigne": return self.__computEnseigneTest(codeItem, dbaseItem)
    elif field in ["Enseigne", "Ville", "Site", "Agent", "Bassin"]:
      return unidecode(codeItem.lower()).replace("-", " ") == unidecode(dbaseItem.lower()).replace("-", " ")
    elif field == "Point Feu":
      if codeItem == "N":
        return dbaseItem == ""
      if codeItem == "O":
        return dbaseItem == "Point Feu"
    elif field == "Segment Commercial":
      if dbaseItem == "non segmenté" and not codeItem:
        return True
      return dbaseItem != codeItem
    elif field == "Segment Marketing":
      if dbaseItem == "Autres métiers": 
        return codeItem in ["Autres métiers", "Plateforme de redist"]
    elif field in ["Ensemble", "Sous-Ensemble", "PDV"]:
      return codeItem.strip().replace("  ", " ") == dbaseItem.strip().replace("  ", " ")
    print(field, codeItem, dbaseItem, type(codeItem), type(dbaseItem))
    print(index, self.__titles[index + 1], str(codeItem), str(dbaseItem))
    raise(TypeError)


  def __computEnseigneTest(self, codeItem, dbaseItem):
    if codeItem == "BIGMAT FRANCE":
      return dbaseItem == "CMEM"
    elif codeItem == "NEGOCES MATX DE CONSTRUCTION":
      return dbaseItem == "Nég Mtx Cons"
    elif codeItem == "POINT P - MATERIAUX DE CONSTRUCTION":
      return dbaseItem == "SGDB France"
    elif codeItem == "GROUPE(MENT)S REGIONAUX":
      return dbaseItem == "Group. Rég."
    elif codeItem == "BOIS & MATERIAUX":
      return dbaseItem == "Bois & Mat."
    elif codeItem == "NEGOCES AUTRES":
      return dbaseItem == "Autres"
    return unidecode(codeItem.lower()).replace("-", " ") == unidecode(dbaseItem.lower()).replace("-", " ")


