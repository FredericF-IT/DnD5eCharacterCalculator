from re import search
from copy import deepcopy

from Weapons import Weapon
from Attributes import Attributes, AttributeType
from Features import Feature, Value
from Races import Race
from BattleStats import BattleStats
from Classes import Class, ClassList
from Actions import Action

class Character:
    def __init__(self, attr: Attributes, race: Race, weapon: Weapon, actions: set[Action], startingClass: Class, isEmpty:bool=False) -> None:
        if(isEmpty):
            return
        self.attr = attr
        self.damageHistory = []
        self.gottenFeatures = []
        self.battleStats = BattleStats(weapon)
        self.race = race
        self.actions = actions
        self.applyFeatures(race.getRaceFeatures())
        self.attr.addStatBonus(race.getStatBonus())
        self.classes = ClassList(startingClass, self)
        assert len(self.classes.classesInOrderTaken) == 1
        if not (self.attr.choices == ""):
            self.attr.calculateChoices() # character has applied his feautures now, so we always know if they have some first level stat choice.

    def makeCharacter(attr: Attributes, battleStats: BattleStats, race: Race, actions: Action, classes: ClassList, gottenFeatures: list[Feature], damageHistory: list[int]):
        newChar = Character(None, None, None, None, None, True)
        newChar.attr = attr
        newChar.battleStats = battleStats
        newChar.race = race
        newChar.actions = actions
        newChar.classes = classes
        newChar.gottenFeatures = gottenFeatures
        newChar.damageHistory = damageHistory
        return newChar

    def applyFeatures(self, features: list): #, addToFeatureList:bool=False
        #if(addToFeatureList): self.gottenFeatures.extend([feature.name for feature in features])
        for feature in features:
            Feature.applyFeature(feature, self)

    def increaseClass(self, newClassLevel: Class):
        self.battleStats.levelUp()
        self.classes.increaseClass(newClassLevel, self)

    def printCharacter(self):
        print(self)

    def __str__(self) -> str:
        return  self.race.name +" Level "+ str(self.battleStats.level) + "\n" +\
                str(self.classes)  + "\n" +\
                str(self.attr)  + "\n" +\
                "Feats: "+", ".join([feat for feat in self.gottenFeatures])  + "\n" +\
                ("Has advantage on Attacks.\n" if self.battleStats.getsAdvantage else "") +\
                str(self.battleStats)  + "\n" +\
                str(self.battleStats.weapon)
                

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
        return Character.makeCharacter(self.attr.getCopy(), self.battleStats.getCopy(), self.race, self.actions, self.classes.getCopy(), self.gottenFeatures.copy(), self.damageHistory.copy())
        """copyChar = Character(Attributes([0, 0, 0, 0, 0, 0]), self.race, self.battleStats.weapon, self.actions.copy(), self.classes.classesInOrderTaken[0], True, self.classes.getCopy())
        copyChar.attr = self.attr.getCopy()
        print(self.battleStats)
        print(copyChar.battleStats)
        #copyChar.classes = self.classes.getCopy(copyChar)
        assert self.classes == copyChar.classes
        assert self.attr == copyChar.attr
        assert self.battleStats == copyChar.battleStats
        assert self == copyChar
        return copyChar"""
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Character):
            return NotImplemented
        return  self.attr == __value.attr and \
                self.race == __value.race and \
                self.actions == __value.actions and \
                self.battleStats == __value.battleStats and \
                self.classes == __value.classes