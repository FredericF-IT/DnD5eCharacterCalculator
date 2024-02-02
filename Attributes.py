from math import floor
from enum import Enum

class AttributeType(Enum):
    STR = "Str"
    DEX = "Dex"
    CON = "Con"
    INT = "Int"
    WIS = "Wis"
    CHA = "Cha"

class Usefullness(Enum):
    Main = 0 # Max out this one stat if possible
    Either = 1 # Max out only one of these, dump the other
    Both = 2 # Max out both if possible
    Good = 3 # Improve if no better available
    Okay = 4 # Improve if no better available
    Dump = 5 # Start and keep at this at a score of 8 with a mod of -1


class Attributes:
    """Str = 0 # This is for use in data files, as we can currently only navigate via getattr, witch returns a 
    Dex = 0
    Con = 0
    Int = 0
    Wis = 0
    Cha = 0"""

    
    def makeDict(keys: list, values: list) -> dict[AttributeType, int]:
        dictionary = {}
        for i, key in enumerate(keys):
            dictionary[key] = values[i]
        return dictionary

    def __init__(self, baseStats: list[int]) -> None:
        self.choices = ""
        self.baseStats = Attributes.makeDict(AttributeType, baseStats)
        self.boni = Attributes.makeDict(AttributeType, [0, 0, 0, 0, 0, 0])
        self.mod = Attributes.makeDict(AttributeType, [0, 0, 0, 0, 0, 0])
        self.hasStartingChoice = False
        self.unchoosable = set[AttributeType]()
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
        assert self.getStat(stat) < 21
        self.calcModifier(stat)

    def addStatBonus(self, stats: dict[AttributeType, int]):
        for statName in stats.keys():
            self.ASI(statName, stats[statName])

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
        attr = Attributes(list(self.baseStats.values()))
        attr.addStatBonus(self.boni)
        attr.choices = self.choices
        return attr

    def __str__(self) -> str:
        info = "| Str | Dex | Con | Int | Wis | Cha |\n"
        scores = "| "
        mods = "| "
        for statName in AttributeType:
            scores += '{:2d}'.format(self.getStat(statName)) + "  | "
            mods += '{:2d}'.format(self.mod[statName]) + "  | "
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
                self.choices == __value.choices