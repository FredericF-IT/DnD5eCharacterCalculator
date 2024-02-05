from math import ceil
from Weapons import Weapon

class BattleStats:
    level = 1
    attacksPerAction = 1
    attacksPASource = dict[str, int]()
    extraCritDice = 0
    critRange = 20                          # The number here is where crits start, so 20 means only nat 20, 18 means a crit on 18, 19, or 20 
    firstLevelFeat = False
    profBonus = 2
    flatDamageBonus = 0
    flatToHitBonus = 0
    extraDamageDice = dict[int, int]()      # Damage dice you get to add to every attack you make (like Improved Smite or Elemental Cleaver)
    getsAdvantageAll = False                # Your class has a reliable way to get advantage for every attack
    getsAdvantageFirst = False              # Your class has a reliable way to get advantage for your first attack
    getsWeaponRerolls = False               # Can reroll weapon dice if the roll is a 1 or a 2

    def __init__(self, weapon: Weapon) -> None:
        self.weapon = weapon
        pass

    def levelUp(self):
        self.level += 1
        self.profBonus = ceil(self.level/4) + 1

    def addExtraAttack(self, sourceClass: str):
        self.attacksPASource[sourceClass] = self.attacksPASource.get(sourceClass, 1) + 1
        self.attacksPerAction = max(self.attacksPASource.values())

    def getCopy(self):
        newBattleStats = BattleStats(self.weapon)
        newBattleStats.level = self.level
        newBattleStats.attacksPASource = self.attacksPASource.copy()
        newBattleStats.attacksPerAction = self.attacksPerAction
        newBattleStats.extraCritDice = self.extraCritDice
        newBattleStats.critRange = self.critRange
        newBattleStats.firstLevelFeat = self.firstLevelFeat
        newBattleStats.profBonus = self.profBonus
        newBattleStats.flatDamageBonus = self.flatDamageBonus
        newBattleStats.flatToHitBonus = self.flatToHitBonus
        newBattleStats.weapon = self.weapon
        newBattleStats.extraDamageDice = self.extraDamageDice.copy()
        newBattleStats.getsAdvantageAll = self.getsAdvantageAll
        newBattleStats.getsAdvantageFirst = self.getsAdvantageFirst
        newBattleStats.getsWeaponRerolls = self.getsWeaponRerolls
        return newBattleStats

    def __str__(self) -> str:
        return  "Attacks per action: " + str(self.attacksPerAction) + "\n"+\
                "Crit range: " + str(self.critRange) + " Crit dice: " + str(self.extraCritDice) + "\n"+\
                "Damage bonus: " + str(self.flatDamageBonus) + " toHit bonus " + str(self.flatToHitBonus) + "\n"+\
                "Proficiency Bonus: " + str(self.profBonus) + "\n"+\
                "Other dice: " + ", ".join([str(x[1])+"d"+str(x[0]) for x in self.extraDamageDice.items()])
    
    # Dice can also easily removed by using a negative number oof dice.
    # This is usefull for upgrading features, as you may have an increase from 2d6 to 2d8 etc.
    def addExtraDamageDie(self, dice: list[(int, int)]):
        for numOfDice, diceFace in dice:
            self.extraDamageDice[diceFace] = self.extraDamageDice.get(diceFace, 0) + numOfDice

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, BattleStats):
            return NotImplemented
        return  self.level == __value.level and \
                self.attacksPASource == __value.attacksPASource and \
                self.extraCritDice == __value.extraCritDice and \
                self.critRange == __value.critRange and \
                self.firstLevelFeat == __value.firstLevelFeat and \
                self.profBonus == __value.profBonus and \
                self.flatDamageBonus == __value.flatDamageBonus and \
                self.flatToHitBonus == __value.flatToHitBonus and \
                self.weapon == __value.weapon and \
                self.extraDamageDice == __value.extraDamageDice and \
                self.getsAdvantageAll == __value.getsAdvantageAll and \
                self.getsAdvantageFirst == __value.getsAdvantageFirst and \
                self.getsWeaponRerolls == __value.getsWeaponRerolls