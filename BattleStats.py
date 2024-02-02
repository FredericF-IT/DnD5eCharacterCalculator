from math import ceil
from Weapons import Weapon

class BattleStats:
    level = 1
    attacksPerAction = 1
    attacksPASource = dict[str, int]()
    critDice = 2
    critRange = 20 # The number here is where crits start, so 20 means only nat 20, 18 means a crit on 18, 19, or 20 
    firstLevelFeat = False
    profBonus = 2
    flatDamageBonus = 0
    flatToHitBonus = 0
    extraDamageDice = dict[int, int]()

    def __init__(self, weapon: Weapon) -> None:
        self.weapon = weapon
        pass

    def levelUp(self):
        self.level += 1
        self.profBonus = ceil(self.level/4) + 1

    def addExtraAttack(self, sourceClass: str):
        self.attacksPASource[sourceClass] = self.attacksPASource.get(sourceClass, 1) + 1
        self.attacksPerAction = max(self.attacksPASource.values())


    # Dice can also easily removed by using a negative number oof dice.
    # This is usefull for upgrading features, as you may have an increase from 2d6 to 2d8 etc.
    def addExtraDamageDie(self, dice: list[(int, int)]):
        for numOfDice, diceFace in dice:
            self.extraDamageDice[diceFace] = self.extraDamageDice.get(diceFace, 0) + numOfDice
            self.extraDamageDice = 0
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, BattleStats):
            return NotImplemented
        return  self.level == __value.level and \
                self.attacksPASource == __value.attacksPASource and \
                self.critDice == __value.critDice and \
                self.critRange == __value.critRange and \
                self.firstLevelFeat == __value.firstLevelFeat and \
                self.profBonus == __value.profBonus and \
                self.flatDamageBonus == __value.flatDamageBonus and \
                self.flatToHitBonus == __value.flatToHitBonus and \
                self.weapon == __value.weapon