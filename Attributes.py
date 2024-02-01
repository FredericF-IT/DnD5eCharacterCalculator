from math import floor
from enum import Enum

class AttributeType(Enum):
    STR = "Str"
    DEX = "Dex"
    CON = "Con"
    INT = "Int"
    WIS = "Wis"
    CHA = "Cha"

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
        self.baseStats = Attributes.makeDict(AttributeType, baseStats)
        self.boni = Attributes.makeDict(AttributeType, [0, 0, 0, 0, 0, 0])
        self.mod = Attributes.makeDict(AttributeType, [0, 0, 0, 0, 0, 0])
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

    choices = ""

    def getChoices(self):
        pattern, exception = self.choices.split("E")
        attributes = pattern.split("|")
        #for attribute in attributes:
# TODO do first level feat somewhere
        return
    
    
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