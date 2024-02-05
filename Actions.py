from Attributes import Attributes
from Weapons import Dice, Weapon
from enum import Enum
from Converter import Converter
from BattleStats import BattleStats
from Requirements import Requirement, Requireable

class ActionType(Enum):
    action = 'Action'
    bonusAction = 'Bonus Action'
    onePerTurn = 'Once Per Turn'

def printIf(condition: bool, *text: str):
    if condition: print(*text)

class Action(Requireable):
    hitChanceBook = dict[(int, bool, int), float]()
    critChanceBook = dict[(int, bool), float]()

    #otherDamageDice = []
    useActionDice = False
    useTableDamage = False
    def __init__(self, name: str, resource: ActionType, modToDamage: bool, requirements: list[Requirement], baseWeaponOverride : list[(int, int)], tableName: str) -> None:
        self.name = name
        self.resource = resource
        self.modToDamage = modToDamage
        self.requirements = requirements
        if(not baseWeaponOverride == None):
            self.useActionDice = True
            self.alterDice = (Dice.averageValueForDice(baseWeaponOverride), Dice.averageValueForDiceWithRerolls(baseWeaponOverride))
            diceOnlyOne = [(1, dice[1]) for dice in baseWeaponOverride]
            self.alterDiceOneDie = (Dice.averageValueForDice(diceOnlyOne), Dice.averageValueForDiceWithRerolls(diceOnlyOne))
        if(not tableName == None):
            self.useTableDamage = True
            self.tableName = tableName
            self.tableOwner = Converter.tableData[tableName].ownerClass
            self.alterDiceTable = ([Dice.averageValueForDice(tableEntry) for tableEntry in Converter.tableData[tableName].entryPerLevel], \
                                   [Dice.averageValueForDiceWithRerolls(tableEntry) for tableEntry in Converter.tableData[tableName].entryPerLevel])
            self.alterDiceTableOneDie = ([Dice.averageDamageForDie(dice[0][1], 1) for dice in Converter.tableData[tableName].entryPerLevel], \
                                         [Dice.averageDamageForDieWithRerolls(dice[0][1], 1) for dice in Converter.tableData[tableName].entryPerLevel])

    def initStaticData():
        Action.hitChanceBook = Weapon.caclulateHitChances()
        Action.critChanceBook = Weapon.caclulateCritChances()

    def parseAction(lines: list[str]) -> (ActionType, bool, list[Requirement], int):
        i = 1
        requirements = []
        modToDamage = None # Should always be set, if not there: Error
        damageDieOverride = None
        tableName = None
        while(i < len(lines)):
            lineParts = lines[i].split(" ")
            i += 1
            if(lineParts[0] == "Req:"):
                requirements.append(Requirement(lineParts[1], lineParts[2], lineParts[3], lineParts[4]))
            elif(lineParts[0] == "DamageTable:"):
                tableName = lineParts[1]
            elif(lineParts[0] == "Damage:"):
                typeName, value = lineParts[1].split("=")
                damageDieOverride = Converter.convert(typeName, value)
            elif(lineParts[0] == "ModToDamage:"):
                modToDamage = lineParts[1] == "True"
        return (ActionType(lines[0]), modToDamage, requirements, damageDieOverride, tableName)

    def executeAttack(self, attr: Attributes, battleStats: BattleStats, enemyAC: int, advantage: bool, levelPerClass: int, doPrint:bool=False):
        weapon = battleStats.weapon
        mod = attr.getMod(weapon.usedMod)
        toHit = battleStats.profBonus + mod + battleStats.flatToHitBonus                                          # TODO Add magic item bonus
        hitChance = Action.hitChanceBook[(enemyAC-toHit, advantage, battleStats.critRange)]
        critChance = Action.critChanceBook[(battleStats.critRange, advantage)]
        printIf(doPrint, mod, toHit, enemyAC, hitChance, critChance)
        extraDamageDice = 0
        for (dieFace, dieCount) in battleStats.extraDamageDice.items():
            extraDamageDice += Dice.averageDamageForDie(dieFace, dieCount)
        #alterDiceTable
        weaponDamage = 0
        weaponDamageOneDie = 0
        rerolls = battleStats.getsWeaponRerolls
        if(self.useActionDice):
            weaponDamage = self.alterDice[rerolls]
            weaponDamageOneDie = self.alterDiceOneDie[rerolls]
        elif(self.useTableDamage):
            weaponDamage = self.alterDiceTable[rerolls][levelPerClass[self.tableOwner] - 1]
            extraDamageDice += self.alterDiceTableOneDie[rerolls][levelPerClass[self.tableOwner] - 1]    # Table values are not part of a weapons damage, they come from sources like sneak attack,
                                                                                            # which dont benefit from enhanced crits, so they only get x2
        else:
            weaponDamage = weapon.averageHitDamage[rerolls]
            weaponDamageOneDie = weapon.averageHitDamageOneDie[rerolls]

        straightBonus = mod * self.modToDamage + battleStats.flatDamageBonus
        hitDamage = weaponDamage + extraDamageDice + straightBonus
        critDamage = (weaponDamage + extraDamageDice) * 2 + weaponDamageOneDie * battleStats.extraCritDice + straightBonus
        
        damagePerAttack = critChance * critDamage + (hitChance - critChance) * hitDamage
        
        printIf(doPrint, weaponDamage, weaponDamageOneDie)
        printIf(doPrint, hitDamage, critDamage, straightBonus, extraDamageDice)
        """
        critChance is the likelihood of having a crit side on the die, times the damage done on a crit.
        (hitChance - critChance) gives us the likelihood where we hit and do normal damage.
        straightBonus is not affected by crits, they only double the dice. 
        """

        if(self.name == "Attack"): # Only the basic attack action qualifies for extra attack
            printIf(doPrint, damagePerAttack, battleStats.attacksPerAction)
            return round(damagePerAttack * battleStats.attacksPerAction, 6)
        printIf(doPrint, damagePerAttack)
        return round(damagePerAttack, 6)
    
    def getRequirements(self) -> list[Requirement]:
        return self.requirements
    
    def __str__(self) -> str:
        return self.name + \
            ("\n" if len(self.requirements) > 0 else "") + "\n".join(["  If "+str(req) for req in self.requirements])+\
            "\n  As " + self.resource.value + ":" + \
            "\n    Average dice roll: " + (str(self.alterDice) if self.useActionDice else ("From table "+self.tableName if self.useTableDamage else "Same as weapon dice")) + (" + mod used by weapon" if self.modToDamage else "")