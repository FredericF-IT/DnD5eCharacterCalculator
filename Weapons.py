from scipy import stats
from Attributes import AttributeType

class Dice:
    def parseDice(string: str) -> list[(int, int)]:
        weaponDice = []
        for d in string.split("|"): # For magic weapons, as some have more then one dice type, f.e.: The Flame Tounge Longsword does 1d8 slashing and 2d6 fire damage. 
            numDice, diceFace = d.split("d")
            weaponDice.append((int(numDice), int(diceFace)))
        return weaponDice
    
    def averageDamageForDie(dieFace, dieCount):
        return ((dieFace/2)+0.5)*dieCount
    
    def averageValueForDice(dice: list[(int, int)]):
        averageDamage = 0
        for (dieCount, dieFace) in dice:
            averageDamage += Dice.averageDamageForDie(dieFace, dieCount)
        return averageDamage

class Weapon:
    def __init__(self, wType: str, damageDice: [(int, int)], usedMod: AttributeType) -> None:
        self.wType = wType
        self.damageDice = damageDice
        self.averageHitDamage = Dice.averageValueForDice(damageDice)
        self.usedMod = usedMod
    
    def caclulateHitChances() -> dict[(int, bool, int), float]:
        hitChanceBook = {}
        for diffAcToHit in range(-11, 31):
            for critRange in range(18, 21):
                chance = min(max(21-diffAcToHit, 21-critRange), 19)/20
                hitChanceBook[(diffAcToHit, False, critRange)] = round(chance, 6)
                hitChanceBook[(diffAcToHit, True, critRange)] = round(chance * (2 - chance), 6)
        return hitChanceBook

    def caclulateCritChances() -> dict[(int, bool), float]:
        critChanceBook = {}
        for critRangeStarts in range(18, 21):
            chance = 1-(critRangeStarts-1)/20
            critChanceBook[(critRangeStarts, False)] = round(chance, 6)
            critChanceBook[(critRangeStarts, True)] = round(stats.binom.pmf(1, 2, chance) + stats.binom.pmf(1, 2, chance), 6) # chance of getting 1 crit with two dice + chance of getting 2 crits with two dice
        return critChanceBook
    
    def __str__(self) -> str:
        return self.wType + " " + " + ".join([str(number)+"d"+str(face) for (number, face) in self.damageDice]) + " uses " + self.usedMod.name