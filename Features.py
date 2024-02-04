from Converter import Converter
from copy import deepcopy

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
            assert self.isFinished()
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

class Feature:
    def __init__(self, name: str, varChanges: list[(str, Value)], methodCalls: list[(str, list[Value])], subFeatures: list['Feature'], actions: list) -> None:
        self.name = name
        self.varChanges = varChanges
        self.methodCalls = methodCalls
        self.subFeatures = subFeatures
        self.actions = set(actions)

    def parseFeature(lines: list[str], actionDict: dict) -> (list[(str, Value)], list[(str, list[Value])], list[(str, list[str])]):
        varChanges = []
        methodCalls = []
        subFeatures = []
        actions = []
        
        def getArgumentValues(values: str) -> list[Value]:
            valueList = []
            for valueAndType in values.split("|"):
                value, valueType = valueAndType.split("=")
                valueList.append(Value(value, valueType))
            return valueList

        for line in lines:
            accessType, values = line.split("[")
            if(accessType == "var"):        # var[path value valueType]
                path, value, valueType = values[:-1].split(" ")
                varChanges.append((path, Value(value, valueType)))
            elif(accessType == "method"):     # method[path(value=valueType|value2=valueType2|...)] 
                path, values = values[:-2].split("(")
                methodCalls.append((path, getArgumentValues(values)))
            elif(accessType == "feature"):    # feature[featureName value|value2|...]
                featureName, values = values[:-1].split(" ")
                subFeatures.append((featureName, values.split("|")))  # Sub features should know the type of their holes
            elif(accessType == "action"):    # feature[featureName value|value2|...]
                actionName = values[:-1]
                actions.append(actionDict[actionName])
        return (varChanges, methodCalls, subFeatures, actions)

    def fillInValues(self, holeValues: list[str]):
        for varChange in self.varChanges:
            varChange = varChange[1]
            if varChange.isFinished(): # has all values
                continue
            if(varChange.insertNew(holeValues.pop(0))): # added a value, True if now finished
                continue
            varChange.insertNew(holeValues.pop(0)) # fill second hole, is now always finished

        for methodCall in self.methodCalls:
            for arg in methodCall[1]:
                if arg.isFinished(): # has all values
                    continue
                if(arg.insertNew(holeValues.pop(0))): # added a value, True if now finished
                    continue
                arg.insertNew(holeValues.pop(0)) # fill second hole, is now always finished

        for feature in self.subFeatures: # fills in holes of subfeatures
            feature.fillInValues(holeValues)

    # Feature can not fill in holes of own values, the only missing values are in subfeatures.
    # Not all created features are "finished" at runtime, as they may only appear as filled in subfeatures that are never used on their own. 
    def createFeature(name: str, features: dict[str, 'Feature'], varChanges: list[(str, Value)], methodCalls: list[(str, list[Value])], subFeatures: list[(str, list[str])], actions: list) -> 'Feature':
        filledSubFeatures = []
        for subFeature in subFeatures:
            feature = features[subFeature[0]].getCopy()
            feature.fillInValues(subFeature[1])
            filledSubFeatures.append(feature)
        return Feature(name, varChanges, methodCalls, filledSubFeatures, actions)
        
    def isFinished(self) -> bool:
        for varChange in self.varChanges:
            if(not varChange[1].isFinished()): return False

        for methodArgs in self.methodCalls:
            for value in methodArgs[1]:
                if(not value.isFinished()): return False
        
        for subFeature in self.subFeatures:
            if(not subFeature.isFinished()):   return False

        return True

    def applyFeature(self, character):
        assert self.isFinished()
        for var in self.varChanges:
            value = var[1].getValue()
            #print(value, var, type(value))
            if(isinstance(value, bool)):
                #print(value, var, "worked")
                character.setVariable(var[0], value)
            else:
                #print("huhuh")
                character.setVariable(var[0], character.getVariable(var[0]) + value)
        for methodCall in self.methodCalls:
            character.useMethod(methodCall[0], methodCall[1])
        character.actions = character.actions.union(self.actions)
        for subFeature in self.subFeatures:
            subFeature.applyFeature(character)

    def getCopy(self):
        return Feature(self.name, deepcopy(self.varChanges), deepcopy(self.methodCalls), self.subFeatures.copy(), self.actions.copy()) # first two need deepcopy as they are tuples in a list, the last one is just a list of Values
    
    def __str__(self) -> str:
        return self.name + ":" +\
            ("\n  " + ", ".join([varChange[0]+"="+str(varChange[1]) for varChange in self.varChanges]) if len(self.varChanges) > 0 else "")+\
            ("\n  " + ", ".join([methodCall[0]+"("+", ".join([str(value) for value in methodCall[1]])+")" for methodCall in self.methodCalls]) if len(self.methodCalls) > 0 else "")+\
            ("\n" + "\n".join([("  "+str(subFeature).replace("\n", "\n  ")) for subFeature in self.subFeatures]) if len(self.subFeatures) > 0 else "")