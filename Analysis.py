from Mitosis import CombinationExplorer, Test
from CharSheet import Character
from Actions import Action, ActionType
from CharIO import getFeatures, getRaces, getWeapons, getActions, getFeats, getChoices, getClasses, getSettings, saveBuild
from enum import Enum
from time import time
from math import ceil

# ------                                                  STANDARD SETTINGS                                                   ------ #
onlyGoodStats = True    # Enable to not assign stats in scores that dont increase damage, heavily reducing the amount of starting permutations
maxCharacters = 2000    # The highest number of characters for each class. Using this removes everything but the top x characters
cleanseEvery = 3        # How often characters are reduced. 1 is not recomended as it discourages multiclassing, where features only become strong a few levels in. For can get problematic at levels > 12
levelToReach = 20       # Program continues until characters have reached this level. (2 to 20)
keepOnlyUnique = True   # Kill all characters of same class that do the excact same damage, leaving only one of them.
keepLowerLevels = True  # You can choose to only keep the highest list if you run into RAM problems, but you will not be able to look back at the characters that were best at a specific lower level.
multiProcessing = False # Multiprocessing will allocate wild amounts of RAM, only turn on if your setup works for those settings. 
# ------      ------      ------      ------      ------        ------        ------      ------      ------      ------      ------ #

(onlyGoodStats, maxCharacters, cleanseEvery, levelToReach, keepOnlyUnique, multiProcessing) = getSettings()

if(levelToReach > 20 or levelToReach < 2):
    print("\nPlease use a level between 2 and 20 (inclusive). Change in settings file.")
    exit(0)

if(cleanseEvery < 1):
    print("\nPlease use a cleanse frequency higher then 0. Change in settings file.")
    exit(0)



expectedAC = [13, 13, 13, 14, 15, 15, 15, 16, 16, 17, 17, 17, 18, 18, 18, 18, 19, 19, 19, 19]

levelLists = [list[(int, (Character, Action, Action))]() for i in range(0, 20)] # First value is damage, the actions are the best action / bonus action available that resulted in that rounds damage.

def rankBuilds(characters: list[Character], targetList: list[(int, Character)]):
    level = len(characters[0].classes.classesInOrderTaken)-1
    print("Ranking level", str(level+1)+"...")
    acAtLevel = expectedAC[level]
    for character in characters:
        bestActMain = None
        bestActMainValue = 0
        bestActBonus = None
        bestActBonusValue = 0
        perRoundDamage = 0
        freeAction = []
        for action in character.actions:
            if not (action.isAvailable(character)): # Rogues get Sneak Attack at first level, but only get advantage reliably at second level.
                continue 
            damage = action.executeAttack(character.attr, character.battleStats, acAtLevel, character.battleStats.getsAdvantageAll, character.classes.levelOfClasses)
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
            elif(action.resource == ActionType.onePerTurn):
                perRoundDamage += damage
                freeAction.append(action)
        perRoundDamage += round(bestActMainValue + bestActBonusValue, 6)
        character.damageHistory.append(perRoundDamage)
        targetList.append((perRoundDamage, (character.classes.classesInOrderTaken[0], character, bestActMain, bestActBonus, freeAction)))
    targetList.sort(key=lambda entry: entry[0], reverse=True)

    if (maxCharacters == None or (level) % cleanseEvery > 0):
        print("Skipped level", level+1, "culling.")
        return characters
    characters = []
    keepEntries = []
    for aClass in classes.values():
        charactersLeft = maxCharacters
        haveSeenDamage = {}
        for entry in targetList:
            if not (entry[1][0].name == aClass.name):
                continue
            if(level > 0 and keepOnlyUnique): # We want variety at the first level
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
    targetList.extend(keepEntries)
    targetList.sort(key=lambda entry: entry[0], reverse=True)
    print(str(len(characters)) + " survive.")
    return characters

class characterSelection(Enum):
    BestAtEnd = 0 # Compare the builds that have the highest damage at the final level
    BestAtLevel = 1 # Compare the builds by getting the best one at each level

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk

def getBestPerClass(listIndex: int) -> list[(list[list[int]], list[list[int]])]:
    perClassData = []
    for aClass in classes.values():
        listEnd = levelLists[listIndex]
        top5Different = [(0, None)]
        actionUses = []
        i = 1
        while(len(top5Different) < 6 and i < len(listEnd)):
            entry = listEnd[i]
            i += 1
            damage = entry[0]
            if entry[1][0].name == aClass.name and not (damage == top5Different[-1][0]):
                top5Different.append((damage, entry[1][1]))
                actionUses.append(getDamageString(entry))

        top5Different.pop(0)

        buildText = []
        buildDamage = []
        buildHistory = []
        for i, character in enumerate(top5Different):
            characterStr = str(character[1])
            buildText.append("Build "+str(i+1)+" does "+actionUses[i]+"\n\n"+characterStr)
            buildDamage.append(character[1].damageHistory)
            buildHistory.append(characterStr+getProgressionString(character[1]))
        perClassData.append((buildText, buildDamage, buildHistory))
    return perClassData

def getProgressionString(character: Character):
    result = "\nThey had level progression:\n  "+"\n  ".join([str(i+1)+". "+bClass.name for i, bClass in enumerate(character.classes.classesInOrderTaken)])
    result += "\nThey got these features:\n  "+"\n  ".join([feature for feature in character.gottenFeatures])
    result += "\nThey got these stat increases:\n"+character.asiHistory
    return result

def showDifferentResults(listIndex: int, mode: characterSelection):
    perClassData = getBestPerClass(listIndex)

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
        currentIndex[0] = 0 # Set to first Character in case there are less builds (all have same damage, happens on low settings)
        buildTextLabel.configure(text=buildText[currentIndex[0]])
        buildTextLabel.grid(row=0,column=0,columnspan=2)
        plotBuilds(perClassData, classIndex[0], currentIndex[0], canvas, toolbar, figure)

    def printCharHistory(perClassData: list[list[str]], classIndex: list[int], currentIndex: list[int]):
        buildHistory = perClassData[classIndex[0]][2][currentIndex[0]]
        buildName = input("Give a name fo the file: ")
        saveBuild(buildHistory, buildName)
        print(buildHistory)
        
    def savePlotImage():
        imageName = input("Give a name fo the file: ")
        plt.savefig("./Saved Builds/"+imageName+".eps", format="eps")

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
            canvas[0].get_tk_widget().grid(row=0,column=2,rowspan=2, columnspan=3)


    buildTextLabel = tk.Label(window, text=perClassData[classIndex[0]][0][currentIndex[0]], font='Courier 14', justify="left")
    buildTextLabel.grid(row=0,column=0,columnspan=2)

    nextBuild = tk.Button(window, text="Next Build", font='Courier 14', width=15, height=2, bg="lightgrey", fg="black", command=lambda : swapBuild(currentIndex, True, buildTextLabel, perClassData, classIndex, listIndex, canvas, toolbar, figure))
    lastBuild = tk.Button(window, text="Last Build", font='Courier 14', width=15, height=2, bg="lightgrey", fg="black", command=lambda : swapBuild(currentIndex, False, buildTextLabel, perClassData, classIndex, listIndex, canvas, toolbar, figure))

    lastBuild.grid(row=1,column=0)
    nextBuild.grid(row=1,column=1)

    nextClass = tk.Button(window, text="Next Starting Class", font='Courier 14', width=22, height=2, bg="lightgrey", fg="black", command=lambda : swapClass(currentIndex, True, buildTextLabel, perClassData, classIndex, listIndex, canvas, toolbar, figure))
    lastClass = tk.Button(window, text="Last Starting Class", font='Courier 14', width=22, height=2, bg="lightgrey", fg="black", command=lambda : swapClass(currentIndex, False, buildTextLabel, perClassData, classIndex, listIndex, canvas, toolbar, figure))

    lastClass.grid(row=2,column=0)
    nextClass.grid(row=2,column=1)

    saveButton = tk.Button(window, text="Save .txt", font='Courier 14', width=10, height=2, bg="lightgrey", fg="black", command=lambda : printCharHistory(perClassData, classIndex, currentIndex))
    saveButton.grid(row=2,column=2)

    imageButton = tk.Button(window, text="Save .eps", font='Courier 14', width=10, height=2, bg="lightgrey", fg="black", command=lambda : savePlotImage())
    imageButton.grid(row=2,column=3)

    quitButton = tk.Button(window, text="Exit", font='Courier 14', width=10, height=2, bg="lightgrey", fg="black", command=window.destroy)
    quitButton.grid(row=2,column=4)


    plotBuilds(perClassData, classIndex[0], currentIndex[0], canvas, toolbar, figure)

    window.mainloop()

def timePretty(seconds: int) -> str:
    secondsReal = ceil(seconds) % 60
    minutes = round(seconds / 60)
    minutesReal = minutes % 60
    hours = round(minutes / 60)
    return str(hours).zfill(2)+"h"+str(minutesReal).zfill(2)+"m"+str(secondsReal).zfill(2)+"s"

def getDamageString(entry):
    character = entry[1]
    extraAttack = character[2].name == "Attack"
    return str(round(entry[0], 6)) + " damage using:\n" + character[2].name + (" x"+str(character[1].battleStats.attacksPerAction) if extraAttack else "") + \
        (" and "+character[3].name if not character[3] == None else "") + \
        ("\nAdding "+", ".join([freeAction.name for freeAction in character[4]]) if len(character[4]) > 0 else "")

def printLevelResults(listIndex: int):  
    print("Top 10 at Level "+str(listIndex+1)+":")   
    for entry in levelLists[listIndex][:10]:
        print(getDamageString(entry))
        entry[1][1].printCharacter()
        print("")
    print("We now have", len(characters), "characters.")
#    input("...")

if __name__ == "__main__":
    actions = getActions()
    features = getFeatures(actions)
    races = getRaces(features)
    weapons = getWeapons()
    feats = getFeats(actions, features)
    choices = getChoices(features)
    classes = getClasses(features, choices)

    startTime = time()
    combi = CombinationExplorer(feats.values(), weapons.values(), races.values(), classes.values())
    characters = combi.createCharactersLvl1(actions, onlyGoodStats)
    print("Calculating damage...")
    print("Level 1...")
    print("We now have", len(characters), "characters. "+("(Only the strongest "+str(maxCharacters)+" survive per class)" if not maxCharacters == None else ""))
    characters = rankBuilds(characters, levelLists[0])
    #printLevelResults(0)
    currentTime = time()
    print("Time so far:", timePretty(currentTime - startTime)+"\n")
    for i in range(1, levelToReach):
        if not (keepLowerLevels):
            levelLists[i-1].clear()
        print("Level "+str(i+1)+"...")
        if(multiProcessing):
            characters = Test.upgradeCharacterLevel(list(classes.values()), list(feats.values()), characters)
        else:
            characters = CombinationExplorer.upgradeCharacterLevel(list(classes.values()), list(feats.values()), characters)
        print("We now have", len(characters), "characters. "+("(Only the strongest "+str(maxCharacters)+" survive per class)" if not (maxCharacters == None or (i) % cleanseEvery > 0) else ""))
        characters = rankBuilds(characters, levelLists[i])
        #printLevelResults(i)
        currentTime = time()
        print("Time so far:", timePretty(currentTime - startTime)+"\n")
    #printLevelResults(levelToReach-1)
    
    keepGoing = True
    while(keepGoing):
        level = input("Choose the level of which you want to see the results.\n(Culled characters still exist at those levels)\nWrite Stop to exit or any number from 2 to "+str(levelToReach)+": ")
        if(level.lower() == "stop"):
            break
        try:
            level = int(level)
            if(level < 2 or level > levelToReach):
                print("Level not in range, please try again.\n")
            else:
                showDifferentResults(level-1, characterSelection.BestAtEnd)
        except:
            print("Unrecognized input: "+str(level))
        print("\n\n")