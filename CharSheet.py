from re import search
from copy import deepcopy

from Weapons import Weapon
from Attributes import Attributes, AttributeType
from Features import Feature, Value
from Races import Race
from BattleStats import BattleStats
from Classes import Class, ClassList

class Character:
    def __init__(self, attr: Attributes, race: Race, weapon: Weapon, actions: set, startingClass: Class) -> None:
        self.attr = attr
        self.gottenFeatures = []
        self.battleStats = BattleStats(weapon)
        self.race = race
        self.actions = actions
        self.attr.addStatBonus(race.getStatBonus())
        self.applyFeatures(race.getRaceFeatures())
       # self.applyFeatures(startingClass.getFeaturesAtLevel(0))
        self.classes = ClassList(startingClass, self)
        assert len(self.classes.classesInOrderTaken) == 1
        if(not self.attr.choices == ""):
            self.attr.calculateChoices() # character has applied his feautures now, so we always know if they have some first level stat choice.

    def applyFeatures(self, features: list, addToFeatureList:bool=False):
        if(addToFeatureList): self.gottenFeatures.extend(features)
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
        for variable in path.split("/"):
            current = getattr(current, variable)
        return current    

    def setVariable(self, path: str, newValue):
        current = self
        allVars = path.split("/")
        lastStep = allVars.pop()
        for variable in allVars:
            current = getattr(current, variable)
        setattr(current, lastStep, newValue)    
        
    def useMethod(self, path: str, values: list[Value]):
        current = self
        allVars = path.split("/")
        funcName = allVars.pop()
        for variable in allVars:
            current = getattr(current, variable)
        arguments = [argument.getValue() for argument in values]
        return getattr(current, funcName)(*arguments) # Gives all (if any) arguments to the method and executes it
        
    def getDictValue(self, path: str, keys: list[Value]):
        current = self
        allVars = path.split("/")
        dictName = allVars.pop()
        for variable in allVars:
            current = getattr(current, variable)
        arguments = [argument.getValue() for argument in keys]
        if(len(arguments) > 1):
            arguments = set(arguments)
        return getattr(current, dictName)[arguments]

    def setDictValue(self, path: str, keys: list[Value], newValue):
        current = self
        allVars = path.split("/")
        dictName = allVars.pop()
        for variable in allVars:
            current = getattr(current, variable)
        arguments = [argument.getValue() for argument in keys]
        if(len(arguments) > 1):
            arguments = set(arguments)
        getattr(current, dictName)[arguments] = newValue

    def getCopy(self) -> 'Character':
        #copyChar = deepcopy(self)
        newAttr = self.attr.getCopy()
        newAttr.boni = Attributes.makeDict(AttributeType, [0, 0, 0, 0, 0, 0])
        newAttr.choices = ""
        copyChar = Character(newAttr, self.race, self.battleStats.weapon, self.actions.copy(), self.classes.classesInOrderTaken[0])
        
        assert self.classes == copyChar.classes
        assert len(copyChar.classes.classesInOrderTaken) == len(self.classes.classesInOrderTaken) 
        assert self == copyChar
        #for i, bonus in enumerate(copyChar.attr.boni.values()):
        #    assert bonus == self.attr.boni.values()[i]
        #copyChar.attr = self.attr.getCopy()
        #copyChar.battleStats = self.battleStats.getCopy()
        #self.classes.getCopy(copyChar)
        return copyChar
    

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Character):
            return NotImplemented
        return  self.attr == __value.attr and \
                self.race == __value.race and \
                self.actions == __value.actions and \
                self.battleStats == __value.battleStats and \
                self.classes == __value.classes