from Converter import Value
from BonusDamage import BonusDamage

from copy import deepcopy

class Feature:
    def __init__(self, name: str, varChanges: list[(str, Value)], methodCalls: list[(str, list[Value])], subFeatures: list['Feature'], actions: list, bonusDamage: list[BonusDamage]) -> None:
        self.name = name
        self.varChanges = varChanges
        self.methodCalls = methodCalls
        self.subFeatures = subFeatures
        self.actions = set(actions)
        self.bonusDamage = bonusDamage

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
    def createFeature(features: dict[str, 'Feature'], name: str, varChanges: list[(str, Value)], methodCalls: list[(str, list[Value])], subFeatures: list[(str, list[str])], actions: list, bonusDamage: list[str]) -> 'Feature':
        filledSubFeatures = []
        for subFeature in subFeatures:
            feature = features[subFeature[0]].getCopy()
            feature.fillInValues(subFeature[1])
            filledSubFeatures.append(feature)
        return Feature(name, varChanges, methodCalls, filledSubFeatures, actions, bonusDamage)
        
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
        for var in self.varChanges:
            value = var[1].getValue()
            if(isinstance(value, bool)):
                character.setVariable(var[0], value)
            else:
                character.setVariable(var[0], character.getVariable(var[0]) + value)
        for methodCall in self.methodCalls:
            character.useMethod(methodCall[0], methodCall[1])
        character.actions = character.actions.union(self.actions)
        for subFeature in self.subFeatures:
            subFeature.applyFeature(character)
        character.battleStats.bonusDamage.extend(self.bonusDamage)

    def getCopy(self):
        return Feature(self.name, [*self.varChanges], deepcopy(self.methodCalls), [*self.subFeatures], self.actions.copy(), [*self.bonusDamage]) # first two need deepcopy as they are tuples in a list, the last one is just a list of Values
    
    def __str__(self) -> str:
        return self.name + ":" +\
            ("\n  " + ", ".join([varChange[0]+"="+str(varChange[1]) for varChange in self.varChanges]) if len(self.varChanges) > 0 else "")+\
            ("\n  " + ", ".join([methodCall[0]+"("+", ".join([str(value) for value in methodCall[1]])+")" for methodCall in self.methodCalls]) if len(self.methodCalls) > 0 else "")+\
            ("\n  " + ", ".join([str(bonus) for bonus in self.bonusDamage]) if len(self.bonusDamage) > 0 else "")+\
            ("\n" + "\n".join([("  "+str(subFeature).replace("\n", "\n  ")) for subFeature in self.subFeatures]) if len(self.subFeatures) > 0 else "")