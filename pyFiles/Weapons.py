from .Attributes import AttributeType

class Dice:
    def parseDice(string: str) -> list[tuple[int, int]]:
        weaponDice = list[tuple[int, int]]()
        for d in string.split("|"): # For magic weapons, as some have more then one dice type, f.e.: The Flame Tounge Longsword does 1d8 slashing and 2d6 fire damage. 
            numDice, diceFace = d.split("d")
            weaponDice.append((int(numDice), int(diceFace)))
        return weaponDice
    
    def averageDamageForDie(dieFace, dieCount):
        return ((dieFace / 2) + 0.5) * dieCount
    
    def averageDamageForDieWithRerolls(dieFace, dieCount):
        normalDamage = (dieFace / 2) + 0.5
        rerollExtra = (dieFace - 2) / dieFace
        return (normalDamage + rerollExtra)*dieCount
    
    def averageValueForDice(dice: list[tuple[int, int]]):
        averageDamage = 0
        for (dieCount, dieFace) in dice:
            averageDamage += Dice.averageDamageForDie(dieFace, dieCount)
        return averageDamage
    
    def averageValueForDiceWithRerolls(dice: list[tuple[int, int]]):
        averageDamage = 0
        for (dieCount, dieFace) in dice:
            averageDamage += Dice.averageDamageForDieWithRerolls(dieFace, dieCount)
        return averageDamage

class Weapon:
    def __init__(self, wType: str, damageDice: list[tuple[int, int]], usedMod: AttributeType) -> None:
        self.wType = wType
        self.damageDice = damageDice
        self.averageHitDamage = (Dice.averageValueForDice(damageDice), Dice.averageValueForDiceWithRerolls(damageDice))
        diceOnlyOne = [(1, x[1]) for x in damageDice]
        self.averageHitDamageOneDie = (Dice.averageValueForDice(diceOnlyOne), Dice.averageValueForDiceWithRerolls(diceOnlyOne)) # Crit bonuses only apply to one damage die, meaning a crit with +1 crit dice on a 2d6 sword does 5d6, not 6d6.
        self.usedMod = usedMod
    
    def caclulateHitChances() -> dict[tuple[int, bool, int], float]:
        hitChanceBook = dict[tuple[int, bool, int], float]()
        for diffAcToHit in range(-11, 31):
            for critRange in range(18, 21):
                chance = min(max(21-diffAcToHit, 21-critRange), 19)/20
                """
                chance = min(max(21-diffAcToHit, 21-critRange), 19)/20
                We start with 21-diffAcToHit, where diffAcToHit is enemyAC - toHit, as it reduces the amount of entries in the hashmap TODO check performance diff of just calculating more entries with less lookup time later
                This gives us the amount of sides on the d20 that would allow us to hit our target.
                As a critical hit (20 on the die, possibly 18 or 19 with some classes) will always be a hit, we take the maximum of our sides that can hit and the number of sides that result in a crit.
                With this, we account for hitting even if there are no sides on our dice that would be high enough to normally hit (AC of 21 with +0 to hit would be impossible without crits.)
                Then we take the minimum of that and 19, as a 1 on the die is always a miss, no matter how good your toHit is.
                Devide our number of sides by 20, and we have our hitchance!
                """
                hitChanceBook[(diffAcToHit, False, critRange)] = round(chance, 6) # We round as floats like too produce "errors" here, like 65.00000001% hit chance.
                hitChanceBook[(diffAcToHit, True, critRange)] = round(chance * (2 - chance), 6)
        return hitChanceBook

    def caclulateCritChances() -> dict[tuple[int, bool], float]:
        critChanceBook = dict[tuple[int, bool], float]()
        for critRangeStarts in range(18, 21):
            chance = 1-(critRangeStarts-1)/20
            critChanceBook[(critRangeStarts, False)] = round(chance, 6)
            critChanceBook[(critRangeStarts, True)] = round(chance * (2 - chance), 6)
        return critChanceBook
    
    def __str__(self) -> str:
        return self.wType + " " + " + ".join([str(number)+"d"+str(face) for (number, face) in self.damageDice]) + " uses " + self.usedMod.name