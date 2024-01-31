import os
from Features import Feature
from CharSheet import Character
from Features import Feature
from Races import Race
from Attributes import Attributes
from Weapons import Weapon, Dice
from Action import Action
from Feats import Feat

def getFiles(folder: str) -> list[str]:
    return [file for file in os.listdir("./"+folder) if file.split('.')[1] == "data"]

def parseRace(lines: list[str], races: dict[str, Race], allFeatures: dict[str, Feature]):
    i = 2
    subracesLeft = True
    while(subracesLeft):
        name = lines[i-1]
        stats = [0,0,0,0,0,0]
        features = []
        if(len(lines) > i+1 and lines[i+1] == "Stats"):
            i += 2
            line = lines[i]
            while(line != "-----------"):
                attr, value = line.split(" ")

                if(attr == "All"):
                    stats = [stat+1 for stat in stats]
                else:
                    stats[Attributes.ATTRS[attr]] = int(value)
                i += 1
                line = lines[i]
        if(len(lines) > i+1 and lines[i+1] == "Features"):
            i += 2
            line = lines[i]
            while(line != "-----------"):
                featureName, value = line.split(" ")
                feature = allFeatures[featureName].getCopy()
                feature.supplyValues([value])
                features.append(feature)
                i += 1
                line = lines[i]
        subracesLeft = len(lines) > i+3 and lines[i+2] == "Type"
        i += 4
        races[name] = Race(name, stats, features)

def getRaces(allFeatures: dict[str, Feature]) -> dict[str, Race]:
    races = {}
    for file in getFiles("Races"):
        with open("./Races/"+file) as f:
            parseRace([file.rstrip() for file in f.readlines()], races, allFeatures)
    return races


def getFeatures() -> dict[str, Feature]:
    features = {}
    for file in getFiles("Features"):
        with open("./Features/"+file) as f:
            name = file.split(".")[0]
            (effects, values) = Feature.parseEffectsValues(f.readlines())
            features[name] = Feature(name, effects, values)
    return features

def getWeapons() -> dict[str, Weapon]:
    weapons = {}
    with open("./Tables/Weapons.data") as f:
        for line in f.readlines():
            wType, diceString = line.rstrip().split(" ")
            weapons[wType] = Weapon(wType, Dice.parseDice(diceString))
    return weapons

def getActions() -> dict[str, Action]:
    actions = {}
    for file in getFiles("Actions"):
        with open("./Actions/"+file) as f:
            name = file.split(".")[0]
            f = [file.rstrip() for file in f.readlines()]
            (resource, addStrToDamage, requirements, damageDieOverride) = Action.parseAction(f)
            actions[name] = Action(name, resource, addStrToDamage, requirements, damageDieOverride)
    return actions

def getFeats(actions: dict[str, Action], features: dict[str, Feature]) -> dict[str, Feat]:
    feats = {}
    for fileName in getFiles("Feats"):
        with open("./Feats/"+fileName) as file:
            name = fileName.split(".")[0]
            lines = [file.rstrip() for file in file.readlines()]
            feats[name] = Feat(name, lines, actions, features)
    return feats

def printDict(dictionary: dict):
    for key in dictionary.keys():
        print(dictionary[key])

features = getFeatures()
printDict(features)
print("\n")
races = getRaces(features)
printDict(races)
print("\n")

weapons = getWeapons()
printDict(weapons)
print("\n")

actions = getActions()
printDict(actions)
print("\n")


feats = getFeats(actions, features)
printDict(feats)
print("\n")

def CreateVariants(races: dict[str, Race], weapons: dict[str, Weapon]):
    return

def testAvailable(actions: list[Action], character: Character):
    print("Using:", character.battleStats.weapon.wType)
    for action in actions:
        print(("  Can get " if action.isAvailable(character) else "  Can't get ") + action.name)
    print("")


chare = Character(Attributes([15, 14, 15, 8, 8, 10]), races["Dragonborn"], weapons["Greataxe"], set([actions["Attack"]]))
chareB = Character(Attributes([15, 14, 15, 8, 8, 10]), races["Half-Orc"], weapons["Polearm"], set([actions["Attack"]]))
chareC = Character(Attributes([15, 14, 15, 8, 8, 10]), races["Dragonborn"], weapons["Light"], set([actions["Attack"]]))

testAvailable(actions.values(), chare)
testAvailable(actions.values(), chareB)
testAvailable(actions.values(), chareC)

chareB.printCharacter()

chareB.battleStats.flatDamageBonus += 2
print("Before", chareB.battleStats.flatDamageBonus, chareB.battleStats.flatToHitBonus)
print(actions["Attack"].executeAttack(chareB.attr, chareB.battleStats, 19, False))
print(actions["Attack"].executeAttack(chareB.attr, chareB.battleStats, 9, False))
feats["Great Weapon Master"].applyToCharacter(chareB)
print("After", chareB.battleStats.flatDamageBonus, chareB.battleStats.flatToHitBonus)
print(actions["Attack"].executeAttack(chareB.attr, chareB.battleStats, 19, False))
print(actions["Attack"].executeAttack(chareB.attr, chareB.battleStats, 9, False))