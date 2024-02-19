import tkinter as tk
from typing import Any, Callable

from .CharIO import CharIO
from .CharSheet import Character
from .Attributes import positions, AttributeType
from .Mitosis import skillCost, scoreBuyableWithPoints

class CharChoice:
    class Option:
        def __init__(self, text: str, optionsNames: list[str], selected: tk.StringVar, row: int, column: int, flavorText: dict[str, str] = None, onChange: Callable = None, available: int = None) -> None:
            self.text = text            # Will be printed as option Name
            length = max([len(name) for name in optionsNames])
            self.optionNames = [text+": "+name.rjust(length) for name in optionsNames] if not text == "" else optionsNames
            self.available = len(optionsNames) if available == None else available
            self.selected = selected
            self.row = row
            self.column = column
            self.flavorText = flavorText
            self.dropDown = None
            self.onChange = onChange

        def draw(self, window: tk.Tk):
            #column, row = self.column, self.row
            #if not(text == ""):
            #    nameLabel = tk.Label(window, text=perClassData[classIndex[0]][0][currentIndex[0]], font=('Courier New', 14), justify="left")
            #    buildTextLabel.grid(row=0,column=0,columnspan=2)
                
            self.dropDown = tk.OptionMenu(window, self.selected, *self.optionNames[:self.available], command=lambda stringVar: self.onChange(stringVar.replace(self.text+":", "").lstrip(), self))
            self.dropDown.grid(row=self.row, column=self.column)
            self.dropDown.configure(font=('Courier New', 14), width=15, height=2)

    def __init__(self, options: list[Option]) -> None:
        self.options = options

    def draw(self, window: tk.Tk):
        for option in self.options:
            option.draw(window)
    
    def clean(self):
        for option in self.options:
            option.dropDown.destroy()
            option.dropDown = None

class ChoiceWindow:
    def __init__(self, name, window: tk.Tk, choice: CharChoice = None, next: 'ChoiceWindow' = None, last: 'ChoiceWindow' = None): 
        self.choice = choice
        self.name = name
        self.next = next
        self.last = last
        self.window = window
        self.nextWindow, self.lastWindow = None, None

    def clean(self):
        self.choice.clean()
        if not (self.last == None):   
            self.lastWindow.destroy()
            self.lastWindow = None
        if not (self.next == None):   
            self.nextWindow.destroy()
            self.nextWindow = None

    def draw(self):
        maxRow = 0
        maxColumn = 0
        for option in self.choice.options:
            option.draw(self.window)
            maxRow = max(maxRow, option.row)
            maxColumn = max(maxColumn, option.column)
        if not (self.last == None):   
            self.lastWindow = tk.Button(self.window, text="Go to "+self.last.name, font=('Courier New', 14), width=15, height=2, bg="lightgrey", fg="black", command=lambda : self.goLast())
            self.lastWindow.grid(row = maxRow + 1, column = 0)
        if not (self.next == None):   
            self.nextWindow = tk.Button(self.window, text="Go to "+self.next.name, font=('Courier New', 14), width=15, height=2, bg="lightgrey", fg="black", command=lambda : self.goNext())
            self.nextWindow.grid(row = maxRow + 1, column = maxColumn)

    def getPosition(self):
        parts = self.window.geometry().split("+")
        return (int(parts[1]), int(parts[2]))

    def goNext(self):
        x, y = self.getPosition()
        self.clean()
        self.next.prepareLoop(x, y)

    def goLast(self):
        x, y = self.getPosition()
        self.clean()
        self.last.prepareLoop(x, y)

    def exitLoop(self): 
        self.window.destroy()

    def prepareLoop(self, x: int, y: int): ...
    def getResult(self) -> list: ...

class StatChoiceWindow(ChoiceWindow):
    def __init__(self, name, window: tk.Tk, choice: CharChoice = None, next: ChoiceWindow = None, last: ChoiceWindow = None):
        self.total = [27]
        self.stats = [8 for i in range(0, 6)]

        return super().__init__(name, window, choice, next, last)

    def prepareLoop(self, x: int, y: int):
        #self.window = tk.Tk()
        self.window.winfo_toplevel().title(self.name)

        options = list[CharChoice.Option]()

        values = [str(8+i) for i in range(0, 8)]

        def setAvailable():
            for i, option in enumerate(options):
                currentPoints = skillCost(self.stats[i])
                maxPoints = currentPoints + self.total[0]
                option.available = scoreBuyableWithPoints(maxPoints) - 7

        def update(newValue: str, caller: CharChoice.Option):
            position = positions[AttributeType(caller.text)]
            oldValue = self.stats[position]
            self.total[0] += skillCost(oldValue)
            newValue = int(newValue)
            self.stats[position] = newValue
            self.total[0] -= skillCost(newValue)

            self.choice.clean()
            setAvailable()
            self.choice.draw(self.window)

        options = []
        options.append(CharChoice.Option("Str", values, tk.StringVar(self.window, value="Str: "+str(self.stats[0]).rjust(2)), 0, 0, None, update))
        options.append(CharChoice.Option("Dex", values, tk.StringVar(self.window, value="Dex: "+str(self.stats[1]).rjust(2)), 0, 1, None, update))
        options.append(CharChoice.Option("Con", values, tk.StringVar(self.window, value="Con: "+str(self.stats[2]).rjust(2)), 0, 2, None, update))
        options.append(CharChoice.Option("Int", values, tk.StringVar(self.window, value="Int: "+str(self.stats[3]).rjust(2)), 0, 3, None, update))
        options.append(CharChoice.Option("Wis", values, tk.StringVar(self.window, value="Wis: "+str(self.stats[4]).rjust(2)), 0, 4, None, update))
        options.append(CharChoice.Option("Cha", values, tk.StringVar(self.window, value="Cha: "+str(self.stats[5]).rjust(2)), 0, 5, None, update))

        self.choice = CharChoice(options)

        setAvailable()
        
        self.draw()

        self.window.geometry('+%d+%d'%(x,y)) 
    
    def getResult(self) -> list:
        return self.stats

def test():
    window = tk.Tk()
    
    window1 = StatChoiceWindow("Stats", window)
    window2 = StatChoiceWindow("Stats B", window)
    window3 = StatChoiceWindow("Stats C", window)
    window1.next = window2
    window2.last = window1
    window2.next = window3
    window3.last = window2

    window1.prepareLoop(50, 50)
    window.mainloop()


def createCharacter():
    actions = CharIO.getActions()
    bonusDamage = CharIO.getBonusDamageSources()
    features = CharIO.getFeatures(actions, bonusDamage)
    races = CharIO.getRaces(features)
    weapons = CharIO.getWeapons()
    choices = CharIO.getChoices(features)
    feats = CharIO.getFeats(actions, features, choices)
    classes = CharIO.getClasses(features, choices)
    test()
    #window = tk.Tk()
    
    #statsWindow = StatChoiceWindow("Stats", window)
