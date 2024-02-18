from math import floor
from enum import Enum

class AttributeType(Enum):
    STR = "Str"
    DEX = "Dex"
    CON = "Con"
    INT = "Int"
    WIS = "Wis"
    CHA = "Cha"
    
positions = {
    AttributeType.STR: 0,
    AttributeType.DEX: 1,
    AttributeType.CON: 2,
    AttributeType.INT: 3,
    AttributeType.WIS: 4,
    AttributeType.CHA: 5,
}

class Usefullness(Enum):
    Main = 0 # Max out this one stat if possible
    Either = 1 # Max out only one of these, dump the other
    Both = 2 # Max out both if possible
    Good = 3 # Improve if no better available
    Okay = 4 # Improve if no better available
    Dump = 5 # Start and keep at this at a score of 8 with a mod of -1


class Attributes:

    def makeDict(keys: list, values: list) -> dict[AttributeType, int]:
        dictionary = {}
        for i, key in enumerate(keys):
            dictionary[key] = values[i]
        return dictionary

    character = None

    def __init__(self, baseStats: list[int], choices:str="", getX:int=0, inY:int=0, unchoosable=set[AttributeType](), hasStartingChoice:bool=False, boni=None) -> None:
        self.choices = choices
        self.ASIAvailable = False
        self.baseStats = Attributes.makeDict(AttributeType, baseStats)
        if boni == None:
            self.boni = Attributes.makeDict(AttributeType, [0, 0, 0, 0, 0, 0])
        else:
            self.boni = boni
        self.mod = Attributes.makeDict(AttributeType, [0, 0, 0, 0, 0, 0])
        self.hasStartingChoice = hasStartingChoice
        self.unchoosable = unchoosable
        self.getX, self.inY = getX, inY
        for statName in AttributeType:
            self.calcModifier(statName)

    def calcModifier(self, stat: AttributeType):
        self.mod[stat] = floor((self.getStat(stat)-10)/2) # Modifier is 0 at score of 10, increases / decreases per +2 / -2

    def getMod(self, stat: AttributeType):
        return self.mod[stat]

    def getStat(self, stat: AttributeType):
        return self.baseStats[stat] + self.boni[stat]

    def ASI(self, stat: AttributeType, value: int):
        self.boni[stat] += value
        #assert self.getStat(stat) < 21
        self.calcModifier(stat)
        return (" +" + str(value) + " " + stat.value)

    def addStatBonus(self, stats: dict[AttributeType, int]):
        historyBuffer = "  Level " + str(self.character.classes.charLevel) + ". ("
        for statName in stats.keys():
            historyBuffer += self.ASI(statName, stats[statName])
        self.character.asiHistory += historyBuffer+")\n"

    def setCharacter(self, character):
        self.character = character

    def addStatBonusList(self, stats: list[int]):
        self.addStatBonus(Attributes.makeDict(AttributeType, stats))

    def calculateChoices(self):
        choice = self.choices
        if("E" in choice):
            choice, exceptFor = self.choices.split("E")
            self.unchoosable = set([AttributeType(stat) for stat in exceptFor.split("|")])
        self.getX, self.inY = [int(value) for value in choice.split("In")]
        self.hasStartingChoice = True

    def getCopy(self) -> 'Attributes':
        attr = Attributes([*self.baseStats.values()], self.choices, self.getX, self.inY, self.unchoosable, self.hasStartingChoice, self.boni.copy())
        #assert attr.choices == self.choices
        #assert attr.mod == self.mod
        #assert attr == self
        return attr

    def __str__(self) -> str:
        info = "     | Str | Dex | Con | Int | Wis | Cha |\n"
        base = "Base | "
        scores = "All  | "
        mods = "Mod  | "
        for statName in AttributeType:
            base += '{:2d}'.format(self.baseStats[statName]) + "  | "
            scores += '{:2d}'.format(self.getStat(statName)) + "  | "
            mods += '{:2d}'.format(self.mod[statName]) + "  | "
        info += base + " \n"
        info += scores + "\n"
        info += mods
        return info
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Attributes):
            return NotImplemented
        return  self.choices == __value.choices and \
                self.unchoosable == __value.unchoosable and \
                self.getX == __value.getX and \
                self.inY == __value.inY and \
                self.hasStartingChoice == __value.hasStartingChoice and \
                self.baseStats == __value.baseStats and \
                self.boni == __value.boni and \
                self.choices == __value.choices and \
                self.ASIAvailable == __value.ASIAvailable