from math import ceil
from Weapons import Weapon

class BattleStats:
    level = 1
    attacksPerAction = 1
    attacksPASource = dict[str, int]()
    critDice = 2
    critRange = 20 # The number here is where crits start, so 20 means only nat 20, 18 means a crit on 18, 19, or 20 
    firstLevelFeat = 0
    profBonus = 2
    flatDamageBonus = 0
    flatToHitBonus = 0

    def __init__(self, weapon: Weapon) -> None:
        self.weapon = weapon
        pass

    def levelUp(self):
        self.level += 1
        self.profBonus = ceil(self.level/4) + 1

    def addExtraAttack(self, sourceClass: str):
        self.attacksPASource[sourceClass] = self.attacksPASource.get(sourceClass, 1) + 1
        self.attacksPerAction = max(self.attacksPASource.values())