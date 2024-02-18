from .Weapons import Weapon
from .BonusDamage import BonusDamage
from .Attributes import AttributeType

class BattleStats:
    attacksPerAction = 1
    attacksPASource = dict[str, int]()
    extraCritDice = 0
    critRange = 20                                      # The number here is where crits start, so 20 means only nat 20, 18 means a crit on 18, 19, or 20 
    firstLevelFeat = False
    flatToHitBonus = 0
    getsAdvantage = dict[AttributeType, bool]()      # Your class has a reliable way to get advantage for every attack
    getsAdvantageFirst = dict[AttributeType, bool]()    # Your class has a reliable way to get advantage for your first attack
    getsWeaponRerolls = False                           # Can reroll weapon dice if the roll is a 1 or a 2
    
    def __init__(self, weapon: Weapon) -> None:
        self.weapon = weapon
        self.bonusDamage = list[BonusDamage]()
        pass

    def setAdvantageAll(self):
        for attr in AttributeType: 
            self.setAdvantage(attr)

    def setAdvantage(self, type: AttributeType):
        self.getsAdvantage[type] = True
        self.getsAdvantageFirst[type] = True

    def hasAdvantage(self, type: AttributeType):
        return self.getsAdvantage.get(type, False)

    def setAdvantageFirstAll(self):
        for attr in AttributeType: 
            self.setAdvantageFirst(attr)

    def setAdvantageFirst(self, type: AttributeType):
        self.getsAdvantageFirst[type] = True

    def hasAdvantageFirst(self, type: AttributeType):
        return self.getsAdvantageFirst.get(type, False)
    
    def addExtraAttack(self, sourceClass: str):
        self.attacksPASource[sourceClass] = self.attacksPASource.get(sourceClass, 1) + 1
        self.attacksPerAction = max(self.attacksPASource.values())

    def getCopy(self):
        newBattleStats = BattleStats(self.weapon)
        newBattleStats.attacksPASource = self.attacksPASource.copy()
        newBattleStats.attacksPerAction = self.attacksPerAction
        newBattleStats.extraCritDice = self.extraCritDice
        newBattleStats.critRange = self.critRange
        newBattleStats.firstLevelFeat = self.firstLevelFeat
        newBattleStats.flatToHitBonus = self.flatToHitBonus
        newBattleStats.weapon = self.weapon
        newBattleStats.getsAdvantage = self.getsAdvantage.copy()
        newBattleStats.getsAdvantageFirst = self.getsAdvantageFirst.copy()
        newBattleStats.getsWeaponRerolls = self.getsWeaponRerolls
        newBattleStats.bonusDamage = [*self.bonusDamage]
        return newBattleStats

    def __str__(self) -> str:
        return  "Attacks per action: " + str(self.attacksPerAction) + "\n"+\
                "Crit range: " + str(self.critRange) + " Crit dice: " + str(self.extraCritDice) + "\n"+\
                "To Hit bonus: " + str(self.flatToHitBonus) + "\n"
    
    # Dice can also easily removed by using a negative number oof dice.
    # This is usefull for upgrading features, as you may have an increase from 2d6 to 2d8 etc.
    #def addExtraDamageDie(self, dice: list[(int, int)]):
    #    for numOfDice, diceFace in dice:
    #        self.extraDamageDice[diceFace] = self.extraDamageDice.get(diceFace, 0) + numOfDice

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, BattleStats):
            return NotImplemented
        return  self.attacksPASource == __value.attacksPASource and \
                self.extraCritDice == __value.extraCritDice and \
                self.critRange == __value.critRange and \
                self.firstLevelFeat == __value.firstLevelFeat and \
                self.profBonus == __value.profBonus and \
                self.flatToHitBonus == __value.flatToHitBonus and \
                self.weapon == __value.weapon and \
                self.getsAdvantage == __value.getsAdvantage and \
                self.getsAdvantageFirst == __value.getsAdvantageFirst and \
                self.getsWeaponRerolls == __value.getsWeaponRerolls
                #self.flatDamageBonus == __value.flatDamageBonus and \
                #self.extraDamageDice == __value.extraDamageDice and \