from Attributes import AttributeType
from Weapons import Dice

class Table:
    def __init__(self, entryPerLevel: list, ownerClass: str, dataType: str, tableName: str) -> None:
        self.ownerClass = ownerClass
        self.entryPerLevel = entryPerLevel
        self.dataType = dataType
        self.tableName = tableName
    
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
        'attrType' : AttributeType,
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
        Converter.tableData[tableName] = Table([Converter.convert(dataType, value) for value in data.split(", ")], tableOwner, dataType, tableName)

    def parsePaths(lines: list[str], actionDict: dict, bonusDamageDict: dict) -> (list[(str, 'Value')], list[(str, list['Value'])], list[(str, list[str])]):
        varChanges = []
        methodCalls = []
        subFeatures = []
        actions = []
        bonusDamage = []
        
        def getArgumentValues(values: str) -> list[Value]:
            if(values == ""): return []
            valueList = []
            for valueAndType in values.split("|"):
                value, valueType = valueAndType.split("=")
                valueList.append(Value(value, valueType))
            return valueList

        for line in lines:
            accessType, values = line.split("[")
            if(accessType == "var"):            # var[path value valueType]
                path, value, valueType = values[:-1].split(" ")
                varChanges.append((path, Value(value, valueType)))
            elif(accessType == "method"):       # method[path(value=valueType|value2=valueType2|...)] 
                path, values = values[:-2].split("(")
                methodCalls.append((path, getArgumentValues(values)))
            elif(accessType == "feature"):      # feature[featureName value|value2|...]
                featureName, values = values[:-1].split(" ")
                subFeatures.append((featureName, values.split("|")))
            elif(accessType == "action"):       # action[actionName]
                actionName = values[:-1]
                actions.append(actionDict[actionName])
            elif(accessType == "bonusDamage"):  # bonusDamage[bonusDamageSourceName]
                bonusDamageSourceName = values[:-1]
                bonusDamage.append(bonusDamageDict[bonusDamageSourceName])
        return (varChanges, methodCalls, subFeatures, actions, bonusDamage)

class Value:
    convValue = None

    def __init__(self, value: str, typeName: str) -> None:
        if(value == "?"): value = None
        if(typeName == "?"): typeName = None
        self.value = value
        self.typeName = typeName
        if self.isFinished():
            self.convValue = Converter.convert(self.typeName, self.value)

    def getValue(self):
        #assert self.isFinished()
        return self.convValue
    
    def isFinished(self) -> bool:
        return not (self.value == None or self.typeName == None)
    
    def insertNew(self, thing: str) -> bool: # Inserts information from superfeatures in order of existing holes
        if(self.value == None):
            self.value = thing
        elif(self.typeName == None):
            self.typeName = thing
        if self.isFinished():
            self.convValue = Converter.convert(self.typeName, self.value)
            return True
        return False # Tells us if insertion has completed this value
    
    def __str__(self) -> str:
        return ("?" if self.value == None else self.value)+" of type "+("?" if self.typeName == None else self.typeName)