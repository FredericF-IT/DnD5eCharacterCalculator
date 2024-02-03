from Mitosis import CombinationExplorer
from CharSheet import Character
from Actions import Action, ActionType
from CharIO import getFeatures, getRaces, getWeapons, getActions, getFeats, getClasses
#from Classes import Class
from enum import Enum

# ------ Enable to not assign stats in scores that dont increase damage, heavily reducing the amount of starting permutations ------ #
onlyGoodStats = True
maxCharacters = 300 # The highest number of characters for each class. Using this removes everything but the top x characters

# ------      ------      ------      ------      ------        ------        ------      ------      ------      ------      ------ #

features = getFeatures()
races = getRaces(features)
weapons = getWeapons()
actions = getActions()
feats = getFeats(actions, features)
classes = getClasses(features)

expectedAC = [13, 13, 13, 14, 15, 15, 15, 16, 16, 17, 17, 17, 18, 18, 18, 18, 19, 19, 19, 19]

level1 = list[(int, (Character, Action, Action))]() # First value is damage, the actions are the best action / bonus action available that resulted in that rounds damage.
level2 = list[(int, (Character, Action, Action))]()
level3 = list[(int, (Character, Action, Action))]()
level4 = list[(int, (Character, Action, Action))]()
level5 = list[(int, (Character, Action, Action))]()
level6 = list[(int, (Character, Action, Action))]()
levelLists = [level1, level2, level3, level4, level5, level6]

def rankBuilds(characters: list[Character], targetList: list[(int, Character)]):
    acAtLevel = expectedAC[len(characters[0].classes.classesInOrderTaken)-1]
    for character in characters:
        bestActMain = None
        bestActMainValue = 0
        bestActBonus = None
        bestActBonusValue = 0
        for action in character.actions:
            damage = action.executeAttack(character.attr, character.battleStats, acAtLevel, character.battleStats.getsAdvantage)
            if(action.resource == ActionType.action):
                if(damage <= bestActMainValue):
                    continue
                bestActMainValue = damage
                bestActMain = action
            else:
                if(damage <= bestActBonusValue):
                    continue
                bestActBonusValue = damage
                bestActBonus = action
        perRoundDamage = bestActMainValue + bestActBonusValue
        character.damageHistory.append(perRoundDamage)
        targetList.append((perRoundDamage, (character.classes.classesInOrderTaken[0], character, bestActMain, bestActBonus)))
    targetList.sort(key=lambda entry: entry[0], reverse=True)
    #print([e[0] for e in targetList])

    if (maxCharacters == None):
        return
    characters.clear()
    keepEntries = []
    for aClass in classes.values():
        charactersLeft = maxCharacters
        for entry in targetList:
            if not (entry[1][0] == aClass):
                continue
            charactersLeft -= 1
            characters.append(entry[1][1])
            keepEntries.append(entry)
            if(charactersLeft <= 0):
                break
    targetList.clear() # Only keep best entries, but have to resort because we went by class
    targetList.extend(keepEntries)
    targetList.sort(key=lambda entry: entry[0], reverse=True)

#def sortCharactersToClass(self, characters: list[Character]) -> dict[Class, Character]:
#    theDict = {}
#    for aClass in self.classes:
#        theDict[aClass] = []
#    for character in characters:


def printLevelResults(listIndex: int):  
    print("Top 10 at Level "+str(listIndex+1)+":")   
    for entry in levelLists[listIndex][:10]:
        character = entry[1]
        extraAttack = character[2].name == "Attack"
        print(entry[0], "damage using", character[2].name, ("x"+str(character[1].battleStats.attacksPerAction) if extraAttack else ""), ("and "+character[3].name if not character[3] == None else ""))
        #print("actually", character[2].executeAttack(character[1].attr, character[1].battleStats, expectedAC[listIndex], character[1].battleStats.getsAdvantage, True))
        character[1].printCharacter()
        print("")
    print("We now have", len(characters), "characters.")
#    input("...")

class characterSelection(Enum):
    BestAtEnd = 0 # Compare the builds that have the highest damage at the final level
    BestAtLevel = 1 # Compare the builds by getting the best one at each level

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import multiprocessing #threading
import tkinter as tk

def showDifferentResults(listIndex: int, mode: characterSelection):
    listEnd = levelLists[listIndex]
    top5Different = [(listEnd[0][0], listEnd[0][1][1])]
    i = 1
    while(len(top5Different) < 5):
        entry = listEnd[i]
        i += 1
        damage = entry[0]
        if not (damage == top5Different[-1][0]):
            top5Different.append((damage, entry[1][1]))
            print(top5Different[-1], top5Different[-1][0])

    buildText = []
    buildDamage = []
    for i, character in enumerate(top5Different):
        character[1].printCharacter()
        print(character[1].damageHistory, character[0], [j for j in range(listIndex)])
        buildText.append("Build "+str(i+1)+" does "+str(round(character[0], 6))+" damage:\n"+str(character[1]))
        buildDamage.append(character[1].damageHistory)

    window = tk.Tk()

    currentIndex = [0]
    def swapBuild(currentIndex: list[int], forward: bool, buildTextLabel: tk.Label, buildText: list[str], maxLength: int, buildDamage: list[list[int]], canvas, toolbar, figure):
        indexChange = 1 if forward else -1
        currentIndex[0] = ((currentIndex[0] + indexChange) + maxLength) % maxLength
        buildTextLabel.configure(text=buildText[currentIndex[0]])
        buildTextLabel.grid(row=0,column=0,columnspan=2)#.pack()
        plotBuilds(buildDamage.copy(), currentIndex[0], canvas, toolbar, figure)

    canvas = [None]
    toolbar = [None]
    figure = [None]

    def plotBuilds(buildDamage: list[list[int]], currentIndex: int, canvas: list[FigureCanvasTkAgg], toolbar: list[NavigationToolbar2Tk], fig: list[plt.Figure]): # Based on https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
            if(fig[0] == None):
                fig[0] = plt.Figure(figsize = (6, 6), dpi = 100) 

            damagePlot = fig[0].add_subplot(111) 
            levelAxis = [j+1 for j in range(listIndex + 1)]
            currentBuild = buildDamage.pop(currentIndex) 
            i = 0
            for build in buildDamage:
                damagePlot.plot(levelAxis, build, 'k-', label=("Other builds" if i == 0 else None))
                i = 1
            damagePlot.plot(levelAxis, currentBuild, 'r-', label="Build "+str(currentIndex+1))
            
            damagePlot.set_xlabel("Level")
            damagePlot.legend(loc='upper left')

            if(canvas[0] == None):
                canvas[0] = FigureCanvasTkAgg(fig[0], master = window)   
            canvas[0].draw() 
            canvas[0].get_tk_widget().pack#.grid(row=0,column=2,rowspan=2)

            #toolbar_frame = tk.Frame(window) 
            #toolbar_frame.grid(row=0,column=2,rowspan=2) 
            if(toolbar[0] == None):
                toolbar[0] = NavigationToolbar2Tk(canvas[0], toolbar[0], pack_toolbar=False)#toolbar_frame) 
            toolbar[0].update() 

            canvas[0].get_tk_widget().grid(row=0,column=2,rowspan=2)#.pack()
            #toolbar = NavigationToolbar2TkAgg( canvas, toolbar_frame )


    buildTextLabel = tk.Label(window, text=buildText[currentIndex[0]], font='Courier 14', justify="left")
    #buildTextLabel.pack()
    buildTextLabel.grid(row=0,column=0,columnspan=2)
    nextBuild = tk.Button(window, text="Next Build", font='Courier 14', width=15, height=3, bg="blue", fg="yellow", command=lambda : swapBuild(currentIndex, True, buildTextLabel, buildText, listIndex, buildDamage, canvas, toolbar, figure))
    #nextBuild.pack()
    lastBuild = tk.Button(window, text="Last Build", font='Courier 14', width=15, height=3, bg="blue", fg="yellow", command=lambda : swapBuild(currentIndex, False, buildTextLabel, buildText, listIndex, buildDamage, canvas, toolbar, figure))
    #lastBuild.pack()
    lastBuild.grid(row=1,column=0)
    nextBuild.grid(row=1,column=1)
    plotBuilds(buildDamage.copy(), currentIndex[0], canvas, toolbar, figure)

    window.mainloop()
    #displayGraph.join()
    #displayBuilds.join()


if __name__ == "__main__":
    combi = CombinationExplorer(feats.values(), weapons.values(), races.values(), classes.values())
    characters = combi.createCharactersLvl1(actions, onlyGoodStats)
    print("Calculating damage...")
    print("Level 1...")
    rankBuilds(characters, level1)
    #printLevelResults(0)
    
    for i in range(1, 6):
        print("Level "+str(i+1)+"...")
        characters = combi.upgradeCharacterLevel(characters)
        rankBuilds(characters, levelLists[i])
        #printLevelResults(i)

    showDifferentResults(5, characterSelection.BestAtEnd)
