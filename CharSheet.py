from re import search

from Weapons import Weapon
from Attributes import Attributes
from Features import Feature
from Races import Race
from BattleStats import BattleStats
from Classes import Class, ClassList
from Requirements import Converter

class Character:
    def __init__(self, attr: Attributes, race: Race, weapon: Weapon, actions: set, startingClass: Class) -> None:
        self.attr = attr
        self.battleStats = BattleStats(weapon)
        self.race = race
        self.actions = actions
        self.attr.addStatBonus(race.getStatBonus())
        self.applyFeatures(race.getRaceFeatures())
        self.classes = ClassList(startingClass, self)

    def applyFeatures(self, features: list):
        for feature in features:
            Feature.applyFeature(feature, self)

    def increaseClass(self, newClassLevel: Class):
        self.battleStats.levelUp()
        self.classes.increaseClass(newClassLevel, self)

    def printCharacter(self):
        print(self.race.name, self.battleStats.level)
        print(self.classes)
        print(self.attr)
        print(self.battleStats.weapon)


    def getVariable(self, path: str):
        current = self
        allVars = path.split("/")
        lastStep = allVars.pop()
        for variable in allVars:
            current = getattr(current, variable)
        if(search(r'\[.*\]', path)): # TODO maybe remove for performance?
            funcName, value = lastStep.split("[")
            valueStr, valueTypeStr = value[:-1].split("=") # should be /path/dict[value typeOfValue]
            return getattr(current, funcName)[Converter.convert(valueTypeStr, valueStr)]
        elif(search(r'\(.*\)', path)):
            funcName, value = lastStep.split("(")
            valueStr, valueTypeStr = value[:-1].split("=") # should be /path/method(value typeOfValue)
            return getattr(current, funcName)(Converter.convert(valueTypeStr, valueStr))
        else:
            return getattr(current, lastStep)
    
    def setVariable(self, path: str, newValue):
        current = self
        allVars = path.split("/")
        lastStep = allVars.pop()
        for variable in allVars:
            current = getattr(current, variable)
        if(search(r'\[.*\]', lastStep)): # TODO maybe remove for performance?
            funcName, value = lastStep.split("[")
            valueStr, valueTypeStr = value[:-1].split("=") # should be /path/dict[value typeOfValue]
            getattr(current, funcName)[Converter.convert(valueTypeStr, valueStr)] = newValue
       # elif(search(r'(.*)', lastStep)):
       #     valueStr, valueTypeStr = path.split("[")[:1].split("=") # should be /path/method(value typeOfValue)
       #     setattr(current(Converter.convert(valueTypeStr, valueStr)), )
        else:
            setattr(current, lastStep, newValue)