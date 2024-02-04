from Attributes import AttributeType
from Weapons import Dice

class Table:
    def __init__(self, entryPerLevel: list, ownerClass: str) -> None:
        self.ownerClass = ownerClass
        self.entryPerLevel = entryPerLevel
    
    def getEntryByClassList(self, levelPerClass: dict[str, int]):
        level = levelPerClass[self.entryPerLevel]
        return self.entryPerLevel[level]
    
    def getEntryBylevel(self, level: int):
        return self.entryPerLevel[level]

class Converter:
    tableData = dict[str, Table]()

    getType = {
        'str': str,
        'int': int,
        'bool': bool,
        'attrTpye' : AttributeType,
        'dice': Dice,
        'table': None
    }

    def convert(typeName: str, valueStr: str):
        if(typeName == 'table'):
            return Converter.tableData[valueStr]
        if(typeName == 'dice'):
            return Dice.parseDice(valueStr)
        return (Converter.getType[typeName])(valueStr)
    
    def readTable(data: str, tableOwner: str):
        tableName, data = data.split("=")
        dataType, data = data[:-1].split("[")
        Converter.tableData[tableName] = Table([Converter.convert(dataType, value) for value in data.split(", ")], tableOwner)