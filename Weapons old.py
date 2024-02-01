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
    hitChanceBook = {}
    critChanceBook = {}
    wasPrecalculated = False

    def __init__(self, wType: str, damageDice: [(int, int)], usedMod: AttributeType) -> None:
        self.wType = wType
        self.damageDice = damageDice
        self.averageHitDamage = Dice.averageValueForDice(damageDice)
        self.usedMod = usedMod
        if(not Weapon.wasPrecalculated):
            Weapon.wasPrecalculated = True
            Weapon.preCaclulateHitchances()
            Weapon.preCaclulateCritchances()

    def hitChance(enemyAC: int, toHit: int, advantage: bool, critRange: int):
        return Weapon.hitChanceBook[(enemyAC, toHit, advantage, critRange)]
    
    def preCaclulateHitchances():
        for enemyAC in range(9, 20):
            for toHit in range(-3, 11):
                for critRange in range(18, 21):
                    chance = (21-max(min((enemyAC-toHit), critRange), 2))/20
                    Weapon.hitChanceBook[(enemyAC, toHit, True, critRange)] = chance
                    Weapon.hitChanceBook[(enemyAC, toHit, False, critRange)] = chance * (2 - chance)

    def preCaclulateHitchancesB():
        pass

    def preCaclulateCritchances():
        for critRangeStarts in range(18, 21):
            chance = 1-(critRangeStarts-1)/20
            Weapon.critChanceBook[(critRangeStarts, False)] = chance
            Weapon.critChanceBook[(critRangeStarts, True)] = stats.binom.pmf(1, 2, chance) + stats.binom.pmf(1, 2, chance) # chance of getting 1 crit with two dice + chance of getting 2 crits with two dice
            
    def critChance(critRangeStarts:int, advantage: bool):
        return Weapon.critChanceBook((critRangeStarts, advantage))
    
    def __str__(self) -> str:
        return self.wType + " " + " + ".join([str(number)+"d"+str(face) for (number, face) in self.damageDice]) + " uses " + self.usedMod.name

if __name__ == "__main__":
    from random import randint, choice, seed
    from timeit import default_timer as timer

    # Optimizing this and Action.executeAttack will be the most important, as we have to run this for every possible character at every level.
    # I will try to use multithreading for the per character analysis, cutting down the processing time by about 1/<Your number of cores>
    # At 600.000.000 runs my peak used RAM was 13.774 GB just for python (according to task manager)

    # version log (runs == 200.000.000):
    # without hashmap:  81.0
    # ver 1:            64.4 (+20.45% speed increase)
    # ver 2:            55.7 (+16.53% speed increase) # Calculated both advantage and non advantage values at first visit of those values, added advantage bool to keyword tuple
    # ver 3:            42.3 (+14.55% speed increase) # realized theres not that many combinations, so pre-caclulating is possible and better because we dont have to check if key was in dictionary every time
    # From here, we only compare speed of preCalculation method, so the scale will be adjusted. (test_length to 200.000)
    # ver 4:            31.9 (+19.14% speed increase) # this will be the last version, as you cant really get better results by optimizing a method that is called once.
    #                   ^ These don't correlate with the speed increase, as there is run to run variance, so the increase is based on a new run of the older method and may have a different scale
    
    test_length = 200000000
    calculate_runs = False
    if(calculate_runs):
        runsPerGB = 600000000 / 13.774
        YOUR_RAM_GB=32 # <--- Change this, or else
        useable_GB_with_buffer = YOUR_RAM_GB * 0.7
        test_length = round(int(runsPerGB * useable_GB_with_buffer)/100)*100
        print("You will execute", test_length, "runs.")

    seed(42)
    randomACs = []
    randomToHits = []
    critRange = []
    for i in range(int(test_length/100)):
        randomACs.append(randint(9, 19))
        randomToHits.append(randint(-3, 10))
        critRange.append(choice([18, 19, 20]))
    
    # At some point the amount/likelihood of unused combinations becomes very low, so i repeat the list to cut the runtime of setting up the variables
    randomACs = randomACs * 100
    randomToHits = randomToHits * 100
    critRange = critRange * 100
    resultsA = []
    resultsB = []
    test_length_halved = test_length / 2
    Weapon.hitChanceBook = {}

    print("Testing started")
    start = timer()

    Weapon.preCaclulateHitchances()
    for i in range(test_length):
  #      no longer needed, as hit chance is just the Hashtable with O(1) as of ver 3
        Weapon.hitChanceBook[(randomACs[i], randomToHits[i], i < test_length_halved, critRange[i])]
  #      Weapon.preCaclulateHitchances()
        

    end = timer()
    time1 = end - start
    print("Run with hitChance:", end - start)
    Weapon.hitChanceBook = {}
    
    start = timer()

    Weapon.preCaclulateHitchances()
    hitChance = Weapon.hitChanceBook
    for i in range(test_length):
        hitChance[(randomACs[i], randomToHits[i], i < test_length_halved, critRange[i])]
  #      Weapon.preCaclulateHitchancesB()

    end = timer()
    time2 = end - start
    print("Run with hitChanceB:", end - start)
    aIsFaster = time1 < time2
    print(("hitChance" if aIsFaster else "hitChanceB")+" is "+str((((time2-time1) / time2) if aIsFaster else ((time1-time2) / time1))*100)+"% faster")

    Weapon.preCaclulateHitchances()
    a = Weapon.hitChanceBook.copy()
    Weapon.hitChanceBook = {}
    
    Weapon.preCaclulateHitchancesB()
    b = Weapon.hitChanceBook.copy()
    Weapon.hitChanceBook = {}

    for key in a.keys():
        resA = round(a[key], 5)
        resB = round(b[key], 5) 
        if(not resA == resB):
            print("missmatch at", i, resA, resB)
            assert False


    """for i, resA in enumerate(resultsA):
        resA = round(resA, 5)
        resB = round(resultsB[i], 5) 
        if(not resA == resB):
            print("missmatch at", i, resA, resB)
            assert False"""
    # ^^^^ Test correctness when changing the math formula