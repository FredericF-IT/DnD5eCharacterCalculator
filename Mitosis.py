from math import floor
from itertools import permutations
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor

from Feats import Feat
from Weapons import Weapon
from Races import Race
from CharSheet import Character
from Classes import Class
from Attributes import Attributes, AttributeType, Usefullness
from Actions import Action

skillCost = lambda score: score-8 + max(score - 13, 0) # The cost is 0 at 8, and increases by 1 until a score of 13. At 14 and 15 the increase goes to 2. You cannot chose a score higher then 15 in pointbuy.

scoreBuyableWithPoints = lambda points: 8 + min(points, 5) + min(floor(max(points - 5, 0)/2), 2)# How high can i make a score with x points? 
                                                                                         # 8 - 13 with 0 - 5 points
                                                                                         # 14 or 15 with 7 or 9 points
                                                                                         # As max is 15, there can be points left over if the calculated score is bought

positions = {
    AttributeType.STR: 0,
    AttributeType.DEX: 1,
    AttributeType.CON: 2,
    AttributeType.INT: 3,
    AttributeType.WIS: 4,
    AttributeType.CHA: 5,
}

class CombinationExplorer:
    def __init__(self, feats: list[Feat], weapons: list[Weapon], races: list[Race], classes: list[Class]) -> None:
        self.feats = feats
        self.weapons = weapons
        self.races = races
        self.classes = classes

    def putStatAtPosition(score: int, stat: AttributeType, scoreList: list[int]):
        scoreList[positions[stat]] = score
        return scoreList
    
    
    def getGoodStatCombinations(goodStats: list[AttributeType], pointsLeft: int, stats: list[int]): # try different combinations
        statCombinations = []
        for goodStat in goodStats:
            maxInOneScore = scoreBuyableWithPoints(pointsLeft)
            for i in range(max(floor(maxInOneScore / len(goodStats))-3, 8), maxInOneScore+1):
                pointsLeftB = pointsLeft - skillCost(i)
                current = CombinationExplorer.putStatAtPosition(i, goodStat, [*stats])
                copyOfStats = [*goodStats]
                copyOfStats.remove(goodStat)                
                if(len(copyOfStats) == 0):
                    statCombinations.append((pointsLeftB, current))
                else:
                    statCombinations.extend(CombinationExplorer.getGoodStatCombinations(copyOfStats, pointsLeftB, current))
        return statCombinations
    
    seenBefore = dict[(int, list[int]), bool]()

    def getOkayStatCombinations(okayStats: list[AttributeType], pointsLeft: int, stats: list[int]):
        if(len(okayStats) == 0):
            if(not CombinationExplorer.seenBefore.get(tuple(stats), False)):
                CombinationExplorer.seenBefore[tuple(stats)] = True
                #assert pointsLeft == 0
                return [stats]
            return []
        statCombinations = []
        for okayStat in okayStats:
            copyOfStats = [*okayStats]
            copyOfStats.remove(okayStat)
            maxInOneScore = scoreBuyableWithPoints(pointsLeft)
            evenStartPoint = floor(floor(maxInOneScore / len(okayStats))/2)*2
            while(pointsLeft - skillCost(evenStartPoint) > len(copyOfStats) * skillCost(15)): # the leftover stats could not use all points
                evenStartPoint += 2
            for i in range(max(evenStartPoint, 8), maxInOneScore+1, 2):
                pointsLeftB = pointsLeft - skillCost(i)
                current = CombinationExplorer.putStatAtPosition(i, okayStat, [*stats])
                statCombinations.extend(CombinationExplorer.getOkayStatCombinations(copyOfStats, pointsLeftB, current))
        return statCombinations
    
    def createAttributes(self, onlyGoodStats: bool) -> dict[Class, list[Attributes]]:
        attributes = dict[Class, Attributes]()
        for startingClass in self.classes:
            usefullness = startingClass.statUsefullness
            importance = usefullness.values()
            keys = list(usefullness.keys())

            statCombinations = []
            
            if(Usefullness.Main in importance): #should start with this high as possible, although we might not always want to start with an odd number when we could have increased the second best stat
                mainStat = keys[list(importance).index(Usefullness.Main)]

                for i in range (14, 16):
                    pointsLeft = 27 - skillCost(i)
                    statCombinations.append((pointsLeft, CombinationExplorer.putStatAtPosition(i, mainStat, [8,8,8,8,8,8])))

            if(Usefullness.Both in importance): #should start with both high as possible, although we might not always want to start with an odd number when we could have increased the second best stat
                stat1Index = list(importance).index(Usefullness.Both)
                stat2Index = list(importance).index(Usefullness.Both, stat1Index+1)
                mainStats1 = keys[stat1Index]
                mainStats2 = keys[stat2Index]

                for i in range (14, 16):
                    pointsLeft = 27 - skillCost(i)
                    for j in range (14, 16):
                        pointsLeftB = pointsLeft - skillCost(j)
                        stats = CombinationExplorer.putStatAtPosition(i, mainStats1, [8,8,8,8,8,8])
                        stats = CombinationExplorer.putStatAtPosition(j, mainStats2, stats)
                        statCombinations.append((pointsLeftB, stats))

            if(Usefullness.Either in importance): #should start with one as high as possible, although we might not always want to start with an odd number when we could have increased the second best stat
                stat1Index = list(importance).index(Usefullness.Either)
                stat2Index = list(importance).index(Usefullness.Either, stat1Index+1)
                possibleStats1 = keys[stat1Index]
                possibleStats2 = keys[stat2Index]

                for i in range (14, 16):
                    pointsLeft = 27 - skillCost(i)
                    statCombinations.append((pointsLeft, CombinationExplorer.putStatAtPosition(i, possibleStats1, [8,8,8,8,8,8])))

                for i in range (14, 16):
                    pointsLeft = 27 - skillCost(i)
                    statCombinations.append((pointsLeft, CombinationExplorer.putStatAtPosition(i, possibleStats2, [8,8,8,8,8,8])))

            statCombinationsV2 = []
            for statCombination in statCombinations:
                if(Usefullness.Good in importance):
                    pointsLeft = statCombination[0]
                    goodStatsLeft = list(importance).count(Usefullness.Good)
                    goodStats = []
                    lastIndex = 0
                    for i in range(goodStatsLeft):
                        lastIndex = list(importance).index(Usefullness.Good, lastIndex)
                        goodStats.append(keys[lastIndex])
                        lastIndex += 1
                    statCombinationsV2.extend(CombinationExplorer.getGoodStatCombinations(goodStats, pointsLeft, statCombination[1]))
                else:
                    statCombinationsV2.extend(statCombination)

            if not(onlyGoodStats):
                statCombinationsV3 = []
                for statCombination in statCombinationsV2:
                    if(Usefullness.Okay in importance): # Any stat that is not a dump stat can now get some points
                        pointsLeft = statCombination[0]
                        goodStatsLeft = list(importance).count(Usefullness.Okay)
                        goodStats = []
                        lastIndex = 0
                        for i in range(goodStatsLeft):
                            lastIndex = list(importance).index(Usefullness.Okay, lastIndex)
                            goodStats.append(keys[lastIndex])
                            lastIndex += 1
                            
                        statCombinationsV3.extend(CombinationExplorer.getOkayStatCombinations(goodStats, pointsLeft, statCombination[1]))
                    else:
                        statCombinationsV3.append(statCombination)

                for i in range(6):
                    statCombinationsV3 = sorted(statCombinationsV3, key=lambda tup: tup[5-i])

                attributes[startingClass] = [Attributes(stats) for stats in statCombinationsV3]
            else:
                attributes[startingClass] = [Attributes(stats[1]) for stats in statCombinationsV2]
        return attributes
    
    seenvariations = dict[(list[AttributeType], int, int), list[list[int]]]()

    def getPossibleCombinations(possibleScores: list[AttributeType], getPlusX: int, yTimes: int) -> set[tuple[int]]:
        lastVersion = CombinationExplorer.seenvariations.get((possibleScores, getPlusX, yTimes), None)
        if(not lastVersion == None): 
            return lastVersion
        possibleVers = []
        baseVersion = [(getPlusX if i < yTimes else 0) for i in range(6)]
        allVersions = list(set(permutations(baseVersion)))
        possibleSpaces = [0,0,0,0,0,0]
        for i, stat in enumerate(AttributeType):
            if(stat in possibleScores):
                possibleSpaces[i] = getPlusX
        if(len(possibleScores) == yTimes):
            CombinationExplorer.seenvariations[(possibleScores, getPlusX, yTimes)] = [possibleSpaces]
            return [possibleSpaces]

        possibleVers = [version for version in allVersions if all([ver <= possibleSpaces[i] for i, ver in enumerate(allVersions[0])])] # only allow versions that are zero where possibleSpaces is zero
        CombinationExplorer.seenvariations[(possibleScores, getPlusX, yTimes)] = possibleVers
        return possibleVers

    def findPointDistribution(usefullness: list[AttributeType], usefullStats: set[AttributeType], reversedUsefullness, exceptForIn: set[int], getPlusX: int, yTimes: int, character: Character) -> list[Character]:
        possibleImprovements = []
        for stat in usefullStats.difference(exceptForIn):
            if((stat, Usefullness.Either) in usefullness):
                eitherStat = reversedUsefullness[Usefullness.Either]
                whichIsDump = 1
                if (character.attr.getStat(eitherStat[0]) == 8): # check which is the dump stat
                    whichIsDump = 0
                possibleImprovements.extend(CombinationExplorer.getPossibleCombinations(tuple(usefullStats - set([eitherStat[1-whichIsDump]])), getPlusX, yTimes))
            elif((stat, Usefullness.Both) in usefullness):
                bothStats = reversedUsefullness[Usefullness.Both]
                possibleImprovements.extend(CombinationExplorer.getPossibleCombinations(tuple(bothStats), getPlusX, yTimes))
            elif((stat, Usefullness.Main) in usefullness):
                otherStat = reversedUsefullness[Usefullness.Good] # Assumes the class has at least one main and one good / usefull Ability Score
                otherStat.append(stat)
                possibleImprovements.extend(CombinationExplorer.getPossibleCombinations(tuple(otherStat), getPlusX, yTimes))

        newCharacters = []
        seenDict = []
        for improvement in possibleImprovements:
            if(improvement in seenDict):
                continue
            seenDict.append(improvement)
            newCharacter = character.getCopy()
            newCharacter.attr.addStatBonusList(improvement)
            newCharacters.append(newCharacter)
        return newCharacters

    def goodASIAssignment(usefullStats: list[AttributeType], exceptForIn: set[int], character: Character) -> list[Character]:
        possibleImprovements = []
        for stat in usefullStats.difference(exceptForIn):
            scoreLeft = 20 - character.attr.getStat(stat)
            if(scoreLeft > 1): # assign both in same
                improvementFull = [0, 0, 0, 0, 0, 0]
                improvementFull[positions[stat]] = 2
                possibleImprovements.append(improvementFull)
            if(scoreLeft > 0): # assign one here and one in another stat
                improvementHalf = [0, 0, 0, 0, 0, 0]
                improvementHalf[positions[stat]] = 1
                for statB in usefullStats.difference(exceptForIn.union(set([stat]))):
                    scoreLeftB = 20 - character.attr.getStat(statB)
                    if(scoreLeftB >= 1):
                        improvementFull = [*improvementHalf]
                        improvementFull[positions[statB]] = 1
                        possibleImprovements.append(improvementFull)

        newCharacters = []
        seenDict = []
        for improvement in possibleImprovements:
            if(improvement in seenDict):
                continue
            seenDict.append(improvement)
            newCharacter = character.getCopy()
            newCharacter.attr.addStatBonusList(improvement)
            newCharacters.append(newCharacter)

        if(newCharacters == []):
            newCharacters.append(character)
        return newCharacters

    def createCharactersLvl1(self, actions: list[Action], onlyGoodStats) -> list[Character]:
        characters = list[Character]()
        lastCharCount = 0
        attributes = self.createAttributes(onlyGoodStats)
        baseActions = [actions["Attack"]]
        print("Stat combinations per class:")
        for key in attributes.keys():
            print(key.name, "has", len(attributes[key]), "good combinations.")
        print("Stats, Races, Classes, and Weapons, and first level choices:")
        for aClass in self.classes:
            usefullness, usefullStats, reversedUsefullness = aClass.getUsefulls()

            for race in self.races:
                for weapon in self.weapons:
                    actionsIfWeapon = [*baseActions]
                    if(weapon.wType == "Light"):
                        actionsIfWeapon.append(actions["TwoWeaponFighting"])
                    for stats in attributes[aClass]:
                        newCharacter = Character(stats.getCopy(), race, weapon, set(actionsIfWeapon), aClass)

                        newCharacters = []
                        if(newCharacter.battleStats.firstLevelFeat):
                            for feat in self.feats:
                                if(feat.isAvailable(newCharacter)):
                                    improvedCharacter = newCharacter.getCopy()
                                    feat.applyToCharacter(improvedCharacter)
                                    newCharacters.append(improvedCharacter)

                        newCharacterCopy = [*newCharacters] if not newCharacters == [] else [newCharacter]
                        newCharacters.clear()
                        for character in newCharacterCopy:
                            newCharacters.extend(Test.doChoice(character)) # Choices from feats or classes

                        for character in newCharacters:
                            if(newCharacter.attr.hasStartingChoice):
                                characters.extend(CombinationExplorer.findPointDistribution(usefullness, usefullStats, reversedUsefullness, newCharacter.attr.unchoosable, newCharacter.attr.getX, newCharacter.attr.inY, newCharacter))
                            else:
                                characters.append(newCharacter)


            print(aClass.name, "has", len(characters)-lastCharCount, "good combinations.")
            lastCharCount = len(characters)
        for character in [*characters]:
            for stat in AttributeType:
                if(character.attr.getStat(stat) >= 18):
                    print(character.attr.baseStats[stat], character.attr.boni[stat], character.attr.getStat(stat))
                    character.printCharacter()
                    pass
                #assert character.attr.getStat(stat) < 18 # looking good
        return characters
    
    def upgradeCharacterLevel(classes: list[Class], feats: list[Feat], characters: list[Character]) -> list[Character]:
        newCharacters = []

        #oldLength = len(characters)

        for aClass in classes:
            characterClones = [character.getCopy() for character in characters]
            newCharacters.extend(Test.upgradePerClass(feats, characterClones, aClass))
        #assert oldLength <= len(newCharacters)
        return newCharacters
    
cpuCores=cpu_count()

class Test:
    def getCharactersFromXToY(characters: list[Character], From: int, To: int):
        lastX = len(characters) - From              	# We want to start at from, so we remove the elements before from
        charactersSubset = characters[-lastX:]
        keepY = To - From                               # The number of characters to keep after from
        charactersSubset = charactersSubset[:keepY]     # Removing anything after that
        #assert len(charactersSubset) == keepY
        return charactersSubset

    def upgradeCharacterLevel(classes: list[Class], feats: list[Feat], characters: list[Character]) -> list[Character]:
        processes = []
        executor = ProcessPoolExecutor(max_workers=cpuCores)

        oldLength = len(characters)

        for aClass in classes:
            charactersLeft = oldLength
            stepSize = int(floor(charactersLeft/cpuCores))
            for i in range(0, cpuCores):
                charaterSubset = Test.getCharactersFromXToY(characters, i*stepSize, (i+1)*stepSize)
                charactersLeft -= len(charaterSubset)
                processes.append(executor.submit(Test.upgradePerClass, feats, charaterSubset, aClass))
            if(charactersLeft > 0):
                charaterSubset = characters[-charactersLeft:]
                processes.append(executor.submit(Test.upgradePerClass, feats, charaterSubset, aClass))
        newCharacters = []
        for process in processes:
            newCharacters.extend(process.result())
        executor.shutdown()
        #assert oldLength <= len(newCharacters)
        return newCharacters
    
    def upgradePerClass(feats: list[Feat], characters: list[Character], aClass: Class):
        newCharacters =  list[Character]()
        for character in characters:
            if not (aClass.canTakeClass(character)):
                continue
            character.increaseClass(aClass)

            tempCharacters = []
            tempBaseCharacters = Test.doChoice(character) # choice from the class specifically

            for character in tempBaseCharacters:
                if not (character.classes.subClassChoice == ""):
                    for subClass in aClass.subclasses.values():
                        subClassCharacter = character.getCopy()
                        subClassCharacter.classes.chooseSubclass(aClass, subClass, subClassCharacter)
                        tempCharacters.append(subClassCharacter)
                else:
                    tempCharacters.append(character)

            tempBaseCharacters = [*tempCharacters]
            tempCharacters.clear()

            for character in tempBaseCharacters:
                if not (character.attr.ASIAvailable):
                    tempCharacters.append(character)
                    continue
                character.attr.ASIAvailable = False
                
                for feat in feats:
                    if(feat.isAvailable(character) and not feat.name in character.gottenFeatures):
                        featCharacter = character.getCopy()
                        feat.applyToCharacter(featCharacter)
                        tempCharacters.extend(Test.doChoice(featCharacter)) # might get new choice from feat
                
                baseClass = character.classes.classesInOrderTaken[0] # NOTE Might want to change this to aClass to improve the one they are taking this level
                usefullStats = baseClass.mostUsefullAttrTypes
                dumpStats = set(baseClass.reversedUsefullness.get(Usefullness.Dump, []))
                tempCharacters.extend(CombinationExplorer.goodASIAssignment(usefullStats, dumpStats, character))
            newCharacters.extend(tempCharacters)
        return newCharacters
    
    def doChoice(characterBase: Character) ->  list[Character]:
        getsChoice = characterBase.classes.choice
        choiceCharacters = [characterBase]
        if not(getsChoice == []):
            for choice in getsChoice:
                nextChoice = [*choiceCharacters]
                choiceCharacters.clear()
                for choiceCharacter in nextChoice:
                    choiceCharacters.extend(choice.onePerChoice(choiceCharacter))
            for choiceCharacter in choiceCharacters:
                choiceCharacter.classes.choice = []
        if(choiceCharacters == []):
            return [characterBase]
        return choiceCharacters