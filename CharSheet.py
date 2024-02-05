from Weapons import Weapon
from Attributes import Attributes
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
        self.attr.setCharacter(self)
        self.asiHistory = ""
        self.damageHistory = []
        self.gottenFeatures = []
        self.battleStats = BattleStats(weapon)
        self.race = race
        self.actions = actions
        self.applyFeatures(race.getRaceFeatures())
        self.attr.addStatBonus(race.getStatBonus())
        self.classes = ClassList(startingClass, self)
        #assert len(self.classes.classesInOrderTaken) == 1
        if not (self.attr.choices == ""):
            self.attr.calculateChoices() # character has applied his feautures now, so we always know if they have some first level stat choice.

    def makeCharacter(attr: Attributes, battleStats: BattleStats, race: Race, actions: Action, classes: ClassList, gottenFeatures: list[Feature], damageHistory: list[int], asiHistory: str):
        newChar = Character(None, None, None, None, None, True)
        newChar.attr = attr
        newChar.attr.setCharacter(newChar)
        newChar.battleStats = battleStats
        newChar.race = race
        newChar.actions = actions
        newChar.classes = classes
        newChar.gottenFeatures = gottenFeatures
        newChar.damageHistory = damageHistory
        newChar.asiHistory = asiHistory
        return newChar

    def applyFeatures(self, features: list): #, addToFeatureList:bool=False
        #if(addToFeatureList): self.gottenFeatures.extend([feature.name for feature in features])
        #self.gottenFeatures.extend([feature.name for feature in features])
        for feature in features:
            Feature.applyFeature(feature, self)

    def increaseClass(self, newClassLevel: Class):
        self.battleStats.levelUp()
        self.classes.increaseClass(newClassLevel, self)

    def printCharacter(self):
        print(self)

    def __str__(self) -> str:
        return  self.race.name +" Level "+ str(self.battleStats.level) +\
                str(self.classes)  + "\n" +\
                str(self.attr)  + "\n" +\
                (("Feats:\n  "+"\n  ".join([feat for feat in self.gottenFeatures]) + "\n") if len(self.gottenFeatures) > 0 else "") +\
                ("They have advantage on Attacks.\n" if self.battleStats.getsAdvantageAll else "") +\
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
        return Character.makeCharacter(self.attr.getCopy(), self.battleStats.getCopy(), self.race, self.actions.copy(), self.classes.getCopy(), [*self.gottenFeatures], [*self.damageHistory], self.asiHistory)
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Character):
            return NotImplemented
        return  self.attr == __value.attr and \
                self.race == __value.race and \
                self.actions == __value.actions and \
                self.battleStats == __value.battleStats and \
                self.classes == __value.classes