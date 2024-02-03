from Attributes import Attributes
from Weapons import Dice, Weapon
from enum import Enum
from BattleStats import BattleStats
from Requirements import Requirement, Requireable

class ActionType(Enum):
    action = 'Action'
    bonusAction = 'Bonus Action'

def printIf(condition: bool, *text: str):
    if condition: print(*text)

class Action(Requireable):
    hitChanceBook = dict[(int, bool, int), float]()
    critChanceBook = dict[(int, bool), float]()

    #otherDamageDice = []
    ignoreWeaponDice = False
    def __init__(self, name: str, resource: ActionType, modToDamage: bool, requirements: list[Requirement], baseWeaponOverride : list[(int, int)]) -> None:
        self.name = name
        self.resource = resource
        self.modToDamage = modToDamage
        self.requirements = requirements
        if(not baseWeaponOverride == None):
            self.ignoreWeaponDice = True
            self.alterDice = Dice.averageValueForDice(baseWeaponOverride)

    def initStaticData():
        Action.hitChanceBook = Weapon.caclulateHitChances()
        Action.critChanceBook = Weapon.caclulateCritChances()

    def parseAction(lines: list[str]) -> (ActionType, bool, list[Requirement], int):
        i = 1
        requirements = []
        modToDamage = None # Should always be set, if not there: Error
        damageDieOverride = None
        while(i < len(lines)):
            lineParts = lines[i].split(" ")
            i += 1
            if(lineParts[0] == "Req:"):
                requirements.append(Requirement(lineParts[1], lineParts[2], lineParts[3], lineParts[4]))
            elif(lineParts[0] == "Damage:"):
                damageDieOverride = Dice.parseDice(lineParts[1])
            elif(lineParts[0] == "ModToDamage:"):
                modToDamage = lineParts[1] == "True"
        return (ActionType(lines[0]), modToDamage, requirements, damageDieOverride)

    def executeAttack(self, attr: Attributes, battleStats: BattleStats, enemyAC: int, advantage: bool, doPrint:bool=False):
        weapon = battleStats.weapon
        mod = attr.getMod(weapon.usedMod)
        toHit = battleStats.profBonus + mod + battleStats.flatToHitBonus                                          # TODO Add magic item bonus
        hitChance = Action.hitChanceBook[(enemyAC-toHit, advantage, battleStats.critRange)]
        critChance = Action.critChanceBook[(battleStats.critRange, advantage)]
        printIf(doPrint, mod, toHit, enemyAC, hitChance, critChance)
        otherDamageDice = 0
        for (dieCount, dieFace) in battleStats.extraDamageDice.items():
            otherDamageDice += Dice.averageDamageForDie(dieFace, dieCount)
        weaponDamage = (self.alterDice if self.ignoreWeaponDice else weapon.averageHitDamage)
        weaponDamageOneDie = (self.alterDice if self.ignoreWeaponDice else weapon.averageHitDamageOneDie)
        straightBonus = mod * self.modToDamage + battleStats.flatDamageBonus
        hitDamage = weaponDamage + otherDamageDice + straightBonus
        critDamage = weaponDamageOneDie * battleStats.critDice + straightBonus
        
        damagePerAttack = critChance * critDamage + (hitChance - critChance) * hitDamage
        
        printIf(doPrint, weaponDamage, weaponDamageOneDie)
        printIf(doPrint, hitDamage, critDamage, straightBonus, otherDamageDice)
        """
        critChance is the likelihood of having a crit side on the die, times the damage done on a crit.
        (hitChance - critChance) gives us the likelihood where we hit and do normal damage.
        straightBonus is not affected by crits, they only double the dice. 
        """

        if(self.name == "Attack"): # Only the basic attack action qualifies for extra attack
            printIf(doPrint, damagePerAttack, battleStats.attacksPerAction)
            return damagePerAttack * battleStats.attacksPerAction
        printIf(doPrint, damagePerAttack)
        return round(damagePerAttack, 6)
    
    def getRequirements(self) -> list[Requirement]:
        return self.requirements
    
    def __str__(self) -> str:
        return self.name + \
            ("\n" if len(self.requirements) > 0 else "") + "\n".join(["  If "+str(req) for req in self.requirements])+\
            "\n  As " + self.resource.value + ":" + \
            "\n    Average dice roll: " + (str(self.alterDice) if self.ignoreWeaponDice else "same as weapon dice") + (" + mod used by weapon" if self.modToDamage else "")