from scipy import stats

hitChanceBook = {}
critChanceBook = {}
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
    def __init__(self, wType: str, damageDice: [(int, int)]) -> None:
        self.wType = wType
        self.damageDice = damageDice
        self.averageHitDamage = Dice.averageValueForDice(damageDice)

    def hitChance(enemyAC: int, toHit: int, advantage: bool, critRange: int):
        chance = hitChanceBook.get((enemyAC, toHit, critRange), -1)
        if(chance == -1):
            chance = min(max(21-(enemyAC-toHit), 21-critRange), 19)/20
            hitChanceBook[(enemyAC, toHit, critRange)] = chance
        if(advantage):
            chance = chance * 2 - chance ** 2
        return chance

    def critChance(critRangeStarts:int, advantage: bool):
        chance = critChanceBook.get((critRangeStarts, advantage), -1)
        if(chance == -1):
            chance = 1-(critRangeStarts-1)/20
            critChanceBook[(critRangeStarts, False)] = chance
        if(advantage):
            chance = stats.binom.pmf(1, 2, chance) + stats.binom.pmf(1, 2, chance) # chance of getting 1 crit with two dice + chance of getting 2 crits with two dice
            critChanceBook[(critRangeStarts, True)] = chance
        return chance
    
    def __str__(self) -> str:
        return self.wType + " " + " + ".join([str(number)+"d"+str(face) for (number, face) in self.damageDice])