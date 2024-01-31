from math import floor

class Attributes:
    STR=0
    DEX=1
    CON=2
    INT=3
    WIS=4
    CHA=5

    ATTRS={"Str": STR, "Dex": DEX, "Con": CON, "Int": INT, "Wis": WIS, "Cha": CHA}
    ATTRS_INV={STR: "Str", DEX: "Dex", CON: "Con", INT: "Int", WIS: "Wis", CHA: "Cha"}

    def __init__(self, baseStats: list[int]) -> None:
        self.baseStats = baseStats
        self.boni = [0, 0, 0, 0, 0, 0]
        self.mod = [0, 0, 0, 0, 0, 0]
        for statName in range(6):
            self.calcModifier(statName)

    def calcModifier(self, statName: int):
        self.mod[statName] = floor((self.getStat(statName)-10)/2) # Modifier is 0 at score of 10, increases / decreases per +2 / -2

    def getMod(self, statName: int):
        return self.mod[statName]

    def getStat(self, statName: int):
        return self.baseStats[statName] + self.boni[statName]

    def ASI(self, statName: int, value: int):
        self.boni[statName] += value
        assert self.getStat(statName) < 21
        self.calcModifier(statName)

    def addStatBonus(self, stats: list[int]):
        for statName in range(6):
            self.ASI(statName, stats[statName])

    choices = ""

    def getChoices(self):
        pattern, exception = self.choices.split("E")
        attributes = pattern.split("|")
        #for attribute in attributes:

        return
    
    
    def __str__(self) -> str:
        info = "| Str | Dex | Con | Int | Wis | Cha |\n"
        scores = "| "
        mods = "| "
        for statName in range(6):
            scores += '{:2d}'.format(self.getStat(statName)) + "  | "
            mods += '{:2d}'.format(self.mod[statName]) + "  | "
        info += scores + "\n"
        info += mods
        return info