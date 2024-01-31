from Weapons import Weapon
from Attributes import Attributes
from Features import Feature
from Races import Race
from BattleStats import BattleStats

class Character:
    def __init__(self, attr: Attributes, race: Race, weapon: Weapon, actions: set) -> None:
        self.attr = attr
        self.battleStats = BattleStats(weapon)
        self.race = race
        self.actions = actions
        self.attr.addStatBonus(race.getStatBonus())
        self.applyFeatures(race.getRaceFeatures())

    def applyFeatures(self, features: list[Feature]):
        for feature in features:
            feature.applyFeatures(self)

    def printCharacter(self):
        print(self.race.name)
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