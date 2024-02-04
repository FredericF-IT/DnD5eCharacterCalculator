import os
from Features import Feature
from CharSheet import Character
#from Features import Feature
from Races import Race
from Attributes import Attributes, AttributeType
from Requirements import Requireable
from Weapons import Weapon, Dice
from Actions import Action
from Feats import Feat
from Classes import Class
from Converter import Converter

def getFiles(folder: str) -> list[str]:
    return [file for file in os.listdir("./"+folder) if file.split('.')[1] == "data"]

def getFilesAndFolders(folder: str) -> list[str]: # only for better readable folder structure
    files = [file for file in os.listdir("./"+folder) if ('.' in file and file.split('.')[1] == "data")]
    folders = [file for file in os.listdir("./"+folder) if os.path.isdir("./"+folder+"/"+file)]
    for folderName in folders:
        files += [folderName+"/"+file for file in getFilesAndFolders(folder+"/"+folderName)]
    return files

def readTables():
    for file in getFilesAndFolders("Tables/ClassFeatures"):
        with open("./Tables/ClassFeatures/"+file) as f:
            fileOwner = file.split(".")[0]
            for line in f.readlines():
                Converter.readTable(line.rstrip(), fileOwner)

def getFeatures(actionDict: dict[str, Action]) -> dict[str, Feature]:
    neededFeatures = dict[set[str], list[(list, list, list, list)]]()
    for file in getFilesAndFolders("Features"):
        with open("./Features/"+file) as f:
            name = file.split("/")[-1].split(".")[0]
            (varChanges, methodCalls, subFeatures, actions) = Feature.parseFeature([file.rstrip() for file in f.readlines()], actionDict)
            subFeatureNames = tuple([subFeature[0] for subFeature in subFeatures])
            needed = neededFeatures.get(subFeatureNames, [])            # This dict holds the data for features, each feature has a list of features required to build it as its key.
            needed.append((name, varChanges, methodCalls, subFeatures, actions)) # With this we can start with Features that need no data, and then build more featues that build off of these first ones, etc
            neededFeatures[subFeatureNames] = needed
            #(effects, values) = Feature.parseEffectsValues([file.rstrip() for file in f.readlines()])
            #features[name] = Feature(name, effects, values)
    # We can now systematically resolve the Features
            
    #print("hello", len(neededFeatures))
    availableFeatures = dict[str, Feature]()
    #printDict(neededFeatures)
    for feature in neededFeatures[()]: # no sub features required
        availableFeatures[feature[0]] = Feature.createFeature(feature[0], availableFeatures, feature[1], feature[2], feature[3], feature[4])
        #print(feature[0], "is here")
    #printDict(availableFeatures)
    countOfFeatures = sum([len(feature[1]) for feature in neededFeatures.items()])
    neededFeatures.pop((), None)
    #print("hello", len(availableFeatures), len(neededFeatures), countOfFeatures)
    #printDict(neededFeatures)
    #print(neededFeatures.keys())
    #print(neededFeatures.values())
    while len(availableFeatures.items()) < countOfFeatures:
        keys = list(neededFeatures.keys())
        for key in keys: # Gices the list of names of needed subfeatures
            #print(keys)
            if(set(key).issubset(set(availableFeatures.keys()))): # Continue only if all subFeatures are in availableFeatures
                for feature in neededFeatures[key]:
                    availableFeatures[feature[0]] = Feature.createFeature(feature[0], availableFeatures, feature[1], feature[2], feature[3], feature[4])
                neededFeatures.pop(key) # These were resolved and don't need to be tested again

    # All unfinished features are just subfeatures, they should not be used outside of their super-features, so we remove them from our dictionary.
    #for feature in list(availableFeatures.items()):
    #    if not (feature[1].isFinished()):
    #        availableFeatures.pop(feature[0])

    return availableFeatures

def getRaces(allFeatures: dict[str, Feature]) -> dict[str, Race]:
    races = {}
    for file in getFiles("Races"):
        with open("./Races/"+file) as f:
            Race.parseRace([file.rstrip() for file in f.readlines()], races, allFeatures)
    return races

def getWeapons() -> dict[str, Weapon]:
    weapons = {}
    with open("./Tables/Weapons.data") as f:
        for line in f.readlines():
            wType, diceString, modType = line.rstrip().split(" ")
            weapons[wType] = Weapon(wType, Dice.parseDice(diceString), AttributeType(modType))
    return weapons

def getActions() -> dict[str, Action]:
    readTables()
    Action.initStaticData()
    actions = {}
    for file in getFiles("Actions"):
        with open("./Actions/"+file) as f:
            name = file.split(".")[0]
            f = [file.rstrip() for file in f.readlines()]
            (resource, addStrToDamage, requirements, damageDieOverride, damageDieTable) = Action.parseAction(f)
            actions[name] = Action(name, resource, addStrToDamage, requirements, damageDieOverride, damageDieTable)
    return actions

def getFeats(actions: dict[str, Action], features: dict[str, Feature]) -> dict[str, Feat]:
    feats = {}
    for fileName in getFiles("Feats"):
        with open("./Feats/"+fileName) as file:
            name = fileName.split(".")[0]
            lines = [file.rstrip() for file in file.readlines()]
            feats[name] = Feat(name, lines, actions, features)
    return feats

def getClasses(features: dict[str, Feature]) -> dict[str, Class]:
    classes = {}
    for fileName in getFiles("Classes"):
        with open("./Classes/"+fileName) as file:
            name = fileName.split(".")[0]
            lines = [file.rstrip() for file in file.readlines()]
            classes[name] = Class(name, lines, features)
    return classes

if __name__ == "__main__":
    def printDict(dictionary: dict):
        for key in dictionary.keys():
            print(dictionary[key])

    actions = getActions()
    printDict(actions)
    print("\n")

    features = getFeatures(actions)
    printDict(features)
    print("\n")

    races = getRaces(features)
    printDict(races)
    print("\n")

    weapons = getWeapons()
    printDict(weapons)
    print("\n")

    feats = getFeats(actions, features)
    printDict(feats)
    print("\n")

    classes = getClasses(features)
    printDict(classes)
    print("\n")

    def testAvailable(reqThing: list[Requireable], character: Character, isWeapon=True):
        if(isWeapon):
            print("Using:", character.battleStats.weapon.wType)
        for thing in reqThing:
            print(("  Can use " if thing.isAvailable(character) else "  Can't use ") + thing.name)
        print("")

    if(False): # not as usefull
        characters = []
        for weapon in weapons.values():
            characters.append(Character(Attributes([15, 14, 15, 8, 8, 10]), races["Dragonborn"], weapon, set([actions["Attack"]]), classes["Barbarian"]))

        print("Actions for weapons:")
        for chare in characters:
            testAvailable(actions.values(), chare)

        print("Feats for weapons:")
        for chare in characters:
            testAvailable(feats.values(), chare)

    chareSpecial = Character(Attributes([15, 14, 15, 8, 8, 10]), races["Half-Elf"], weapons["Polearm"], set([actions["Attack"]]), classes["Barbarian"])
    chareSpecial.printCharacter()
    print(chareSpecial.attr.ASIAvailable)
    features["ASI"].applyFeature(chareSpecial)
    print(features["ASI"])
    print(chareSpecial.attr.ASIAvailable)
    
    print(" + ".join([str(chareSpecial.battleStats.critDice * number)+"d"+str(face) for (number, face) in chareSpecial.battleStats.weapon.damageDice]), chareSpecial.battleStats.attacksPerAction, "Attacks")
    for i in range(4):
        chareSpecial.increaseClass(classes["Barbarian"])
    chareSpecial.classes.chooseSubclass(classes["Barbarian"], classes["Barbarian"].subclasses["Path of Giants"], chareSpecial)
    print(" + ".join([str(chareSpecial.battleStats.critDice * number)+"d"+str(face) for (number, face) in chareSpecial.battleStats.weapon.damageDice]), chareSpecial.battleStats.attacksPerAction, "Attacks")
    for i in range(9):
        chareSpecial.increaseClass(classes["Barbarian"])
    print(" + ".join([str(chareSpecial.battleStats.critDice * number)+"d"+str(face) for (number, face) in chareSpecial.battleStats.weapon.damageDice]), chareSpecial.battleStats.attacksPerAction, "Attacks")
    for i in range(3):
        chareSpecial.increaseClass(classes["Barbarian"])
    print(" + ".join([str(chareSpecial.battleStats.critDice * number)+"d"+str(face) for (number, face) in chareSpecial.battleStats.weapon.damageDice]), chareSpecial.battleStats.attacksPerAction, "Attacks")
    for i in range(3):
        chareSpecial.increaseClass(classes["Barbarian"])
    print(" + ".join([str(chareSpecial.battleStats.critDice * number)+"d"+str(face) for (number, face) in chareSpecial.battleStats.weapon.damageDice]), chareSpecial.battleStats.attacksPerAction, "Attacks")
    chareSpecial.printCharacter()

    print("Classes for Stats:")
    testAvailable(classes.values(), chareSpecial, False)

    #print("Before", chareSpecial.battleStats.flatDamageBonus, chareSpecial.battleStats.flatToHitBonus)
    #print(actions["Attack"].executeAttack(chareSpecial.attr, chareSpecial.battleStats, 19, False))
    #print(actions["Attack"].executeAttack(chareSpecial.attr, chareSpecial.battleStats, 9, False))
    #feats["Great Weapon Master"].applyToCharacter(chareSpecial)
    #print("After", chareSpecial.battleStats.flatDamageBonus, chareSpecial.battleStats.flatToHitBonus)
    #print(actions["Attack"].executeAttack(chareSpecial.attr, chareSpecial.battleStats, 19, False))
    #print(actions["Attack"].executeAttack(chareSpecial.attr, chareSpecial.battleStats, 9, False))