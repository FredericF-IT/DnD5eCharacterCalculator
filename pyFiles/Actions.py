from enum import Enum

from .Weapons import Dice, Weapon
from .Requirements import Requirement, Requireable
from .BonusDamage import BonusType

class ActionType(Enum):
    action = 'Action'
    bonusAction = 'Bonus Action'

def printIf(condition: bool, *text: str):
    if condition: print(*text)

class Action(Requireable):
    hitChanceBook: dict[(int, bool, int), float]
    critChanceBook: dict[(int, bool), float]

    useActionDice = False
    def __init__(self, name: str, resource: ActionType, modToDamage: bool, requirements: list[Requirement], baseWeaponOverride : list[tuple[int, int]]) -> None:
        self.name = name
        self.resource = resource
        self.modToDamage = modToDamage
        self.requirements = requirements
        if(not baseWeaponOverride == None):
            self.useActionDice = True
            self.alterDice = (Dice.averageValueForDice(baseWeaponOverride), Dice.averageValueForDiceWithRerolls(baseWeaponOverride))
            diceOnlyOne = [(1, dice[1]) for dice in baseWeaponOverride]
            self.alterDiceOneDie = (Dice.averageValueForDice(diceOnlyOne), Dice.averageValueForDiceWithRerolls(diceOnlyOne))

    def initStaticData():
        Action.hitChanceBook = Weapon.caclulateHitChances()
        Action.critChanceBook = Weapon.caclulateCritChances()

    def parseAction(lines: list[str]) -> tuple[ActionType, bool, list[Requirement], int]:
        from .Converter import Converter
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
                typeName, value = lineParts[1].split("=")
                damageDieOverride = Converter.convert(typeName, value)
            elif(lineParts[0] == "ModToDamage:"):
                modToDamage = lineParts[1] == "True"
        return (ActionType(lines[0]), modToDamage, requirements, damageDieOverride)

    def executeAttack(self, character, enemyAC: int, doPrint:bool=False): # Character will not be typed unless needed, as circular import occurs. For testing, uncomment:
        from .CharSheet import Character
        assert type(character) == Character
        isAttack = self.name == "Attack"
        battleStats = character.battleStats
        attr = character.attr
        weapon = battleStats.weapon
        weaponMod = weapon.usedMod
        mod = attr.getMod(weaponMod)
        advantage = battleStats.getsAdvantage.get(weaponMod, False) or (battleStats.getsAdvantageFirst.get(weaponMod, False) and isAttack)
        toHit = character.classes.profBonus + mod + battleStats.flatToHitBonus                                          # TODO Add magic item bonus
        hitChance = Action.hitChanceBook[(enemyAC-toHit, advantage, battleStats.critRange)]
        critChance = Action.critChanceBook[(battleStats.critRange, advantage)]
        #printIf(doPrint, mod, toHit, enemyAC, hitChance, critChance, character.classes.profBonus, battleStats.flatToHitBonus)

        weaponDamage = 0
        weaponDamageOneDie = 0
        rerolls = battleStats.getsWeaponRerolls
        if(self.useActionDice):
            weaponDamage = self.alterDice[rerolls]
            weaponDamageOneDie = self.alterDiceOneDie[rerolls]
        else:
            weaponDamage = weapon.averageHitDamage[rerolls]
            weaponDamageOneDie = weapon.averageHitDamageOneDie[rerolls]
        extraDamageDice = 0
        extraDamageDiceCrit = 0
        extraDamageDiceONCE = 0
        extraDamageDiceCritONCE = 0
        levelPerClass = character.classes.levelOfClasses
        for bonus in battleStats.bonusDamage:
            if(bonus.isAvailable(character)):
                amount, critAmount = bonus.getBonus(levelPerClass, rerolls)
                #printIf(doPrint, amount, critAmount)
                if(bonus.bType == BonusType.onePerHit):
                    extraDamageDice += amount
                    extraDamageDiceCrit += critAmount       # Already doubled only if applicable, rage is same amount in both cases.
                elif(isAttack):                             # Only once per round, so has to be done with attack
                    extraDamageDiceONCE += amount
                    extraDamageDiceCritONCE += critAmount  

        straightBonus = mod * self.modToDamage
        hitDamage = weaponDamage + straightBonus + extraDamageDice
        critDamage = weaponDamage * 2 + weaponDamageOneDie * battleStats.extraCritDice + straightBonus + extraDamageDiceCrit 
        
        damagePerAttack = critChance * critDamage + (hitChance - critChance) * hitDamage
        
        #printIf(doPrint, weaponDamage, weaponDamageOneDie)
        #printIf(doPrint, hitDamage, critDamage, straightBonus, extraDamageDice)
        #printIf(doPrint, extraDamageDiceCrit, battleStats.extraCritDice)
        """
        critChance is the likelihood of having a crit side on the die, times the damage done on a crit.
        (hitChance - critChance) gives us the likelihood where we hit and do normal damage.
        straightBonus is not affected by crits, they only double the dice. 
        """

        if(isAttack): # Only the basic attack action qualifies for extra attack
            bonusPerRound = critChance * extraDamageDiceCritONCE + (hitChance - critChance) * extraDamageDiceONCE
            #printIf(doPrint, damagePerAttack, battleStats.attacksPerAction, bonusPerRound)
            return round(damagePerAttack * battleStats.attacksPerAction + bonusPerRound, 6)
        #printIf(doPrint, damagePerAttack)
        return round(damagePerAttack, 6)
    
    def getRequirements(self) -> list[Requirement]:
        return self.requirements
    
    def __str__(self) -> str:
        return self.name + \
            ("\n" if len(self.requirements) > 0 else "") + "\n".join(["  If "+str(req) for req in self.requirements])+\
            "\n  As " + self.resource.value + ":" + \
            "\n    Average dice roll: " + (str(self.alterDice) if self.useActionDice else "Same as weapon dice") + (" + mod used by weapon" if self.modToDamage else "")