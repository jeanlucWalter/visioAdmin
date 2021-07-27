from django import db
from openpyxl import load_workbook
from pathlib import Path

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
    "Libellé Typologie SAP": "Segment Commercial",
    "Segmentation Portefeuille": "Segment Marketing",
    "Nom niveau 1": "Enseigne",
    "Nom niveau 2": "Ensemble",
    "Nom niveau 3": "Sous_Ensemble",
    "Nom niveau 4": "Site",
    "Point Feu": "Point Feu",
    # "Nb visites F"
    }

  def __init__(self, fileName):
    self.__columnKey = None
    self.__columnField = {}
    self.__errors = []
    self.__dictValues = {}
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

  def listValues(self, tablePdv:dict) -> dict:
    dictXlsx = dict(self.__dictValues)
    lastIndex = len(tablePdv[0]) - 1
    existingPdV = [self.__buildLine(dbaseLine[0], dictXlsx, dbaseLine, lastIndex) for dbaseLine in tablePdv]
    newPdv = [self.__lineBold(line) for line in dictXlsx.values()]
    return existingPdV + newPdv

  def __lineBold(self, line):
    return ['Nouveau'] + [f'<b>{value}</b>' for value in line] + ['<b>Nouvelle valeur</b>']

  def __buildLine(self, code:str, dictXlsx:dict, dbaseLine:list, lastIndex:int):
    if dbaseLine[lastIndex]:
      return ['Réouverture'] + dictXlsx.pop(code) + [dbaseLine[lastIndex]]
    if code in dictXlsx:
      return ['normal'] + dictXlsx.pop(code) + ['']
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


