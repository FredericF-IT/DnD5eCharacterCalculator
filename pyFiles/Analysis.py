from enum import Enum
from time import time
from math import ceil, floor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk

from .Mitosis import CombinationExplorer, Test
from .CharSheet import Character
from .Actions import Action, ActionType
from .Classes import Class
from .CharIO import CharIO

# ------                                                  STANDARD SETTINGS                                                   ------ #
onlyGoodStats = True    # Enable to not assign stats in scores that dont increase damage, heavily reducing the amount of starting permutations
maxCharacters = 1500    # The highest number of characters for each class. Using this removes everything but the top x characters
cleanseEvery = 3        # How often characters are reduced. 1 is not recomended as it discourages multiclassing, where features only become strong a few levels in. For can get problematic at levels > 12
levelToReach = 20       # Program continues until characters have reached this level. (2 to 20)
keepOnlyUnique = True   # Kill all characters of same class that do the excact same damage, leaving only one of them.
keepLowerLevels = False  # You can choose to only keep the highest list if you run into RAM problems, but you will not be able to look back at the characters that were best at a specific lower level.
multiProcessing = False # Multiprocessing will allocate wild amounts of RAM, only turn on if your setup works for those settings. NOTE Deprecated in general
# ------      ------      ------      ------      ------        ------        ------      ------      ------      ------      ------ #

(onlyGoodStats, maxCharacters, cleanseEvery, levelToReach, keepOnlyUnique, multiProcessing) = CharIO.getSettings()

if(levelToReach > 20 or levelToReach < 2):
    print("\nPlease use a level between 2 and 20 (inclusive). Change in settings file.")
    exit(0)

if(cleanseEvery < 1):
    print("\nPlease use a cleanse frequency higher then 0. Change in settings file.")
    exit(0)

expectedAC = [13, 13, 13, 14, 15, 15, 15, 16, 16, 17, 17, 17, 18, 18, 18, 18, 19, 19, 19, 19]

levelLists = [list[(int, (Character, Action, Action))]() for i in range(0, 20)] # First value is damage, the actions are the best action / bonus action available that resulted in that rounds damage.

#displayList = list[(int, (Character, Action, Action))]()

class characterSelection(Enum):
    BestAtEnd = "Highest damage at final level"   # Compare the builds that have the highest damage at the final level
    BestOverall = "Most consistent damage over all levels" # Compare the builds by getting the best one at each level

#def rankBuildsFinally(level: int, mode: characterSelection):
#    global displayList
#    if (mode == characterSelection.BestAtEnd):
#        displayList = [*levelLists[level-1]]
#        return
#    elif (mode == characterSelection.BestOverall):
#        displayList = [*levelLists[level-1]]    # TODO

def rankBuilds(characters: list[Character], targetList: list[(int, Character)], classes: dict[str, Class]):
    level = characters[0].classes.charLevel
    isLastLevel = level == levelToReach
    needsCleanse = isLastLevel or (not (maxCharacters == None) and level > 1 and level % cleanseEvery == 0)
    
    print("Ranking level", str(level)+"...")
    
    acAtLevel = expectedAC[level - 1]
    for character in characters:
        bestActMain = None
        bestActMainValue = 0
        bestActBonus = None
        bestActBonusValue = 0
        perRoundDamage = 0
        for action in character.actions:
            if not (action.isAvailable(character)): # Example: Rogues get Sneak Attack at first level, but only get advantage reliably at second level.
                continue 
            damage = action.executeAttack(character, acAtLevel)
            if(action.resource == ActionType.action):
                if(damage <= bestActMainValue):
                    continue
                bestActMainValue = damage
                bestActMain = action
            elif(action.resource == ActionType.bonusAction):
                if(damage <= bestActBonusValue):
                    continue
                bestActBonusValue = damage
                bestActBonus = action
        perRoundDamage += round(bestActMainValue + bestActBonusValue, 6)
        character.damageHistory.append(perRoundDamage)
        if(isLastLevel or keepLowerLevels or needsCleanse): # Still need to do everything except this, as we want the damageHistory at every level.
            targetList.append((perRoundDamage, (character.classes.classesInOrderTaken[0], character, bestActMain, bestActBonus)))

    if not needsCleanse:
        print("Skipped level", level, "culling.")
        return characters
    
    targetList.sort(key=lambda entry: entry[0], reverse=True)
    
    characters = []
    keepEntries = []
    for aClass in classes.values():
        charactersLeft = maxCharacters
        haveSeenDamage = {}
        for entry in targetList:
            if not (entry[1][0].name == aClass.name):
                continue
            if(level > 1 and keepOnlyUnique): # We want variety at the first level
                damage = round(entry[0], 6)
                if(haveSeenDamage.get(damage, False)):
                    continue
                else:
                    haveSeenDamage[damage] = True
            charactersLeft -= 1
            characters.append(entry[1][1])
            keepEntries.append(entry)
            if(charactersLeft <= 0):
                break
    targetList.clear() # Only keep best entries, but have to re-sort because we went by class
    if(isLastLevel or keepLowerLevels):
        targetList.extend(keepEntries)
        targetList.sort(key=lambda entry: entry[0], reverse=True)
    print(str(len(characters)) + " survive.")
    return characters

def getBestPerClass(level: int, classes: list[Class]) -> list[(list[list[int]], list[list[int]])]:
    #global displayList
    perClassData = []
    for aClass in classes:
        top5Different = [(0, None)]
        actionUses = []
        i = 1
        while(len(top5Different) < 6 and i < len(levelLists[level])):
            entry = levelLists[level][i]
            i += 1
            damage = entry[0]
            if entry[1][0].name == aClass.name and not (damage == top5Different[-1][0]):
                top5Different.append((entry[1][1].damageHistory[level], entry[1][1]))
                actionUses.append(getDamageString(entry))
                
        top5Different.pop(0)

        buildText = []
        buildDamage = []
        buildHistory = []
        for i, character in enumerate(top5Different):
            characterStr = str(character[1])
            bonusDamageStr = character[1].getDamageBonus()
            buildText.append("Build "+str(i+1)+" does "+actionUses[i]+"\n"+bonusDamageStr+"\n\n"+characterStr)
            buildDamage.append(character[1].damageHistory)
            buildHistory.append(characterStr+getProgressionString(character[1]))
        perClassData.append((buildText, buildDamage, buildHistory))
    return perClassData

def getProgressionString(character: Character):
    result = "\nThey had level progression:\n  "+"\n  ".join([str(i+1)+". "+bClass.name for i, bClass in enumerate(character.classes.classesInOrderTaken)])
    result += "\nThey got these features:\n  "+"\n  ".join([feature for feature in character.gottenFeatures])
    result += "\nThey got these stat increases:\n"+character.asiHistory
    return result

def showDifferentResults(listIndex: int, classes: dict[str, Class], mode : characterSelection = characterSelection.BestAtEnd):
    #rankBuildsFinally(listIndex+1, mode)

    perClassData = getBestPerClass(listIndex, classes.values())

    window = tk.Tk()

    currentIndex = [0]
    classIndex = [0]
    def swapBuild(currentIndex: list[int], forward: bool, buildTextLabel: tk.Label, perClassData: list[list[str]], classIndex: list[int], maxLength: int, canvas, toolbar, figure):
        buildText = perClassData[classIndex[0]][0]
        indexChange = 1 if forward else -1
        maxLength = len(buildText)
        currentIndex[0] = ((currentIndex[0] + indexChange) + maxLength) % maxLength
        buildTextLabel.configure(text=buildText[currentIndex[0]])
        buildTextLabel.grid(row=0,column=0,columnspan=2)
        plotBuilds(perClassData, classIndex[0], currentIndex[0], canvas, toolbar, figure)

    def swapClass(currentIndex: list[int], forward: bool, buildTextLabel: tk.Label, perClassData: list[list[str]], classIndex: list[int], maxLength: int, canvas, toolbar, figure):
        maxLength = len(perClassData)
        indexChange = 1 if forward else -1
        classIndex[0] = ((classIndex[0] + indexChange) + maxLength) % maxLength
        buildText = perClassData[classIndex[0]][0]
        currentIndex[0] = 0
        buildTextLabel.configure(text=buildText[currentIndex[0]])
        buildTextLabel.grid(row=0,column=0,columnspan=2)
        plotBuilds(perClassData, classIndex[0], currentIndex[0], canvas, toolbar, figure)

    def printCharHistory(perClassData: list[list[str]], classIndex: list[int], currentIndex: list[int], doPrint: bool):
        buildHistory = perClassData[classIndex[0]][2][currentIndex[0]]
        if (doPrint):
            print(buildHistory)
        else:
            buildName = input("Give a name fo the file: ")
            CharIO.saveBuild(buildHistory, buildName)
        
    def savePlotImage(canvas: list[FigureCanvasTkAgg]):
        imageName = input("Give a name fo the file: ")
        canvas[0].get_tk_widget().postscript(file=CharIO.PARENT_PATH+"Saved Builds/"+imageName+".eps")

    canvas = [None]
    toolbar = [None]
    figure = [None]

    def plotBuilds(perClassData: list[list[list[int]]], classIndex: int, currentIndex: int, canvas: list[FigureCanvasTkAgg], toolbar: list[NavigationToolbar2Tk], fig: list[plt.Figure]): # Based on https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
            if(fig[0] == None):
                fig[0] = plt.Figure(figsize = (6, 6), dpi = 100) 
            else:
                fig[0].clear()
            damagePlot = fig[0].add_subplot(111) 
            levelAxis = [j+1 for j in range(listIndex + 1)]

            buildDamage = [*perClassData[classIndex][1]]

            currentBuild = buildDamage.pop(currentIndex) 
            i = 0
            for build in buildDamage:
                damagePlot.plot(levelAxis, build, 'k-', label=("Other builds" if i == 0 else None))
                i = 1
            damagePlot.plot(levelAxis, currentBuild, 'r-', label="Build "+str(currentIndex+1))
            
            damagePlot.set_xlabel("Level")
            damagePlot.set_ylabel("Damage")
            damagePlot.legend(loc='upper left')
            if(canvas[0] == None):
                canvas[0] = FigureCanvasTkAgg(fig[0], master = window)   

            canvas[0].draw()

            if(toolbar[0] == None):
                toolbar[0] = NavigationToolbar2Tk(canvas[0], toolbar[0], pack_toolbar=False)
            toolbar[0].winfo_toplevel().title(list(classes.keys())[classIndex])
            toolbar[0].update() 
            canvas[0].get_tk_widget().grid(row=0,column=2,rowspan=2, columnspan=4)


    buildTextLabel = tk.Label(window, text=perClassData[classIndex[0]][0][currentIndex[0]], font=('Courier New', 14), justify="left")
    buildTextLabel.grid(row=0,column=0,columnspan=2)

    nextBuild = tk.Button(window, text="Next Build", font=('Courier New', 14), width=15, height=2, bg="lightgrey", fg="black", command=lambda : swapBuild(currentIndex, True, buildTextLabel, perClassData, classIndex, listIndex, canvas, toolbar, figure))
    lastBuild = tk.Button(window, text="Last Build", font=('Courier New', 14), width=15, height=2, bg="lightgrey", fg="black", command=lambda : swapBuild(currentIndex, False, buildTextLabel, perClassData, classIndex, listIndex, canvas, toolbar, figure))

    lastBuild.grid(row=1,column=0)
    nextBuild.grid(row=1,column=1)

    nextClass = tk.Button(window, text="Next Starting Class", font=('Courier New', 14), width=22, height=2, bg="lightgrey", fg="black", command=lambda : swapClass(currentIndex, True, buildTextLabel, perClassData, classIndex, listIndex, canvas, toolbar, figure))
    lastClass = tk.Button(window, text="Last Starting Class", font=('Courier New', 14), width=22, height=2, bg="lightgrey", fg="black", command=lambda : swapClass(currentIndex, False, buildTextLabel, perClassData, classIndex, listIndex, canvas, toolbar, figure))

    lastClass.grid(row=2,column=0)
    nextClass.grid(row=2,column=1)

    printButton = tk.Button(window, text="Print long", font=('Courier New', 14), width=12, height=2, bg="lightgrey", fg="black", command=lambda : printCharHistory(perClassData, classIndex, currentIndex, True))
    printButton.grid(row=2,column=2)

    saveButton = tk.Button(window, text="Save .txt", font=('Courier New', 14), width=12, height=2, bg="lightgrey", fg="black", command=lambda : printCharHistory(perClassData, classIndex, currentIndex, False))
    saveButton.grid(row=2,column=3)

    imageButton = tk.Button(window, text="Save plot", font=('Courier New', 14), width=12, height=2, bg="lightgrey", fg="black", command=lambda : savePlotImage(canvas))
    imageButton.grid(row=2,column=4)

    quitButton = tk.Button(window, text="Exit", font=('Courier New', 14), width=12, height=2, bg="lightgrey", fg="black", command=window.destroy)
    quitButton.grid(row=2,column=5)

    plotBuilds(perClassData, classIndex[0], currentIndex[0], canvas, toolbar, figure)

    window.mainloop()

def timePretty(seconds: int) -> str:
    secondsReal = ceil(seconds) % 60
    minutes = floor(ceil(seconds) / 60)
    minutesReal = minutes % 60
    hours = floor(minutes / 60)
    return str(hours).zfill(2)+"h"+str(minutesReal).zfill(2)+"m"+str(secondsReal).zfill(2)+"s"

def getDamageString(entry):
    character = entry[1]
    extraAttack = character[2].name == "Attack"
    return str(round(entry[0], 6)) + " damage using:\n" + character[2].name + (" x"+str(character[1].battleStats.attacksPerAction) if extraAttack else "") + \
        (" and "+character[3].name if not character[3] == None else "")

def printLevelResults(listIndex: int, characters: list[Character]):  
    print("Top 10 at Level "+str(listIndex+1)+":")   
    for entry in levelLists[listIndex][:10]:
        print(getDamageString(entry))
        entry[1][1].printCharacter()
        print("")
    print("We now have", len(characters), "characters.")

def analyzeClasses():
    actions = CharIO.getActions()
    bonusDamage = CharIO.getBonusDamageSources()
    features = CharIO.getFeatures(actions, bonusDamage)
    races = CharIO.getRaces(features)
    weapons = CharIO.getWeapons()
    choices = CharIO.getChoices(features)
    feats = CharIO.getFeats(actions, features, choices)
    classes = CharIO.getClasses(features, choices)
    classesUnnamed = list(classes.values())

    startTime = time()
    combi = CombinationExplorer(feats.values(), weapons.values(), races.values(), classesUnnamed)
    characters = combi.createCharactersLvl1(actions, onlyGoodStats)
    print("Calculating damage...")
    print("Level 1...")
    print("We now have", len(characters), "characters.")
    characters = rankBuilds(characters, levelLists[0], classes)
    currentTime = time()
    print("Time so far:", timePretty(currentTime - startTime)+"\n")
    for i in range(1, levelToReach):
        print("Level "+str(i+1)+"...")
        if(multiProcessing):
            characters = Test.upgradeCharacterLevel(classesUnnamed, list(feats.values()), characters)
        else:
            characters = CombinationExplorer.upgradeCharacterLevel(classesUnnamed, list(feats.values()), characters)
        print("We now have", len(characters), "characters. "+("(Only the strongest "+str(maxCharacters)+" survive per class)" if not (maxCharacters == None or (i + 1) % cleanseEvery > 0) else ""))
        characters = rankBuilds(characters, levelLists[i], classes)
        currentTime = time()
        print("Time so far:", timePretty(currentTime - startTime)+"\n")
    
    keepGoing = True
    mode = characterSelection.BestAtEnd
    while(keepGoing):
        level = input("Choose the level of which you want to see the results.\n(Culled characters still exist at those levels)\nWrite help for commands or any number from 2 to "+str(levelToReach)+": ")
        levelNorm = level.lower().lstrip().rstrip()
        if(levelNorm in ["exit", "stop"]):
            break
        elif(levelNorm == "swap"):
            mode = characterSelection.BestOverall if mode == characterSelection.BestAtEnd else characterSelection.BestAtEnd
            print("Now ranking by: "+mode.value)
        elif(levelNorm == "help"):
            print("Exit - to return to main menu")
            #print("Swap - to use different ranking mode") NOTE not implemented
        else:
            try:
                level = int(level)
            except:
                print("Unrecognized input: "+str(level))
                continue
            if(level < 2 or level > levelToReach or (level < levelToReach and not keepLowerLevels)):
                print("Level not in range, please try again.\n")
            else:
                #rankBuildsFinally(level, characterSelection.BestOverall)
                showDifferentResults(level-1, classes, mode)
        print("\n\n")