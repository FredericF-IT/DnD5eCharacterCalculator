from Requirements import Requireable, Requirement
from Features import Feature
from Attributes import Usefullness, AttributeType
from Choices import Choice

class SubClass:
    def __init__(self, name, lines: list[str], features: dict[str, Feature], choices: dict[str, Choice]) -> None:
        self.name = name
        self.featuresAtLevel = dict[int, list[Feature]]()
        self.choicesAtLevel = dict[int, list[Choice]]()
        for line in lines:
            words = line.split(" ")
            #assert words[0] == "Lvl:"
            level = int(words[1][:-1])-1
            (featureList, choiceList) = SubClass.parseClassFeatures(features, choices, words)
            self.choicesAtLevel[level] = choiceList
            self.featuresAtLevel[level] = featureList
    
    def parseClassFeatures(features: dict[str, Feature], choices: dict[str, Choice], words: list[str]):
        featureList = []
        choiceList = []
        featureNames = words[2].split("|")
        for featureName in featureNames:
            nameParts = featureName.split(">")
            if(nameParts[0] == "Choice"):
                choiceList.append(choices[nameParts[1]])
                continue
            feature = features[nameParts[0]].getCopy()
            if(len(nameParts) > 1):
                feature.fillInValues(nameParts[1].split(":"))
            featureList.append(feature)
        return (featureList, choiceList)
    
    def __str__(self) -> str:
        return self.name + "\n  Level: "+"\n  Level: ".join([str(pair[0]+1)+": "+", ".join([feature.name for feature in pair[1]]) for pair in self.featuresAtLevel.items()])


class Class(Requireable):
    def __init__(self, name: str, lines: list[str], features: dict[str, Feature], choices: dict[str, Choice]) -> None:
        self.name = name
        self.requirement1 = None
        self.requirement2 = None
        self.reqType = None
        self.featuresAtLevel = dict[int, list[Feature]]()
        self.choicesAtLevel = dict[int, list[Choice]]()
        self.statUsefullness = dict[AttributeType, Usefullness]()
        for stat in AttributeType:
            self.statUsefullness[stat] = Usefullness.Okay
        i = 0 # keep track what lines we've read
        for line in lines:
            if(line == "-----------"):
                break # have now begun subclasses
            i += 1
            words = line.split(" ")
            if(words[0] == "Lvl:"):
                lvlNumber = int(words[1][:-1])
                (featureList, choiceList) = SubClass.parseClassFeatures(features, choices, words)
                if(len(featureList) == 0):
                    self.choicesAtLevel[lvlNumber-1] = choiceList
                else:
                    self.featuresAtLevel[lvlNumber-1] = featureList
            elif(words[0] == "Stats:"):
                for word in words[1:]:
                    stat, usefullness = word.split("=")
                    self.statUsefullness[AttributeType(stat)] = Usefullness[usefullness]
            elif(words[0] == "Req:"):
                self.requirement1 = Requirement(words[1], words[2], words[3], words[4])
            elif(words[0] == "or Req:"):
                self.requirement2 = Requirement(words[1], words[2], words[3], words[4])
                self.reqType = lambda x, y, character: x.testRequirement(character) or y.testRequirement(character)
            elif(words[0] == "and Req:"):
                self.requirement2 = Requirement(words[1], words[2], words[3], words[4])
                self.reqType = lambda x, y, character: x.testRequirement(character) and y.testRequirement(character)
        # Main class is done # we are at -----------
        i += 3
        self.subclasses = dict[str, SubClass]()
        while i < len(lines):
            name = ""
            data = []
            for line in lines[i:]:
                i += 1
                words = line.split(" ")
                if(words[0] == "Name:"):
                    name = " ".join(words[1:])
                elif(line == "-----------"): # next subclass reached
                    break
                else:
                    data.append(line)
            self.subclasses[name] = SubClass(name, data, features, choices)
            #print(self.subclasses[name])
        
        #print(name, [[str(feature) for feature in features[1]] for features in self.featuresAtLevel.items()])
        self.preCalcUsefulls()

    def getFeaturesAtLevel(self, Level: int, subclassName: str):
        features = self.featuresAtLevel.get(Level, [])
        if not (subclassName == None):
            features.extend(self.subclasses[subclassName].featuresAtLevel.get(Level, []))
        return features

    def canTakeClass(self, character) -> bool:
        if(self.reqType == None):
            return self.requirement1.testRequirement(character)
        return self.reqType(self.requirement1, self.requirement2, character)

    def getRequirements(self) -> list[Requirement]:
        if (self.requirement2 == None):
            return [self.requirement1]
        return [self.requirement1, self.requirement2]

    # the names here get a bit confusing, the point is having easy and cheap access to what stats a character should invest in, and the reverse if needed.
    def preCalcUsefulls(self):
        self.mostUsefull = [(stat) for stat in self.statUsefullness.items() if stat[1] in [Usefullness.Main, Usefullness.Both, Usefullness.Either, Usefullness.Good]]
        self.mostUsefullAttrTypes = set([stat[0] for stat in self.mostUsefull])
        reversedUsefullness = dict[Usefullness, list[AttributeType]]()
        for item in self.statUsefullness.items():
            oldValue = reversedUsefullness.get(item[1], [])
            oldValue.append(item[0])
            reversedUsefullness[item[1]] = oldValue
        self.reversedUsefullness = reversedUsefullness

    def getUsefulls(self) -> (list[(AttributeType, Usefullness)], set[AttributeType], dict[Usefullness, list[AttributeType]]):
        return (self.mostUsefull, self.mostUsefullAttrTypes, self.reversedUsefullness)

    def __str__(self) -> str:
        return self.name + \
            "\n  If "+" and ".join([str(req) for req in self.getRequirements()]) + "\n  Features:" + "\n" + \
            "\n".join(["    Level "+str(items[0]+1)+": "+", ".join([feature.name for feature in items[1]]) for items in self.featuresAtLevel.items()])+ \
            ("\nChoices:\n"+"\n".join(["    Level "+str(items[0]+1)+": "+", ".join([choice.name for choice in items[1]]) for items in self.choicesAtLevel.items()]) if len(self.choicesAtLevel.keys()) > 0 else "")

class ClassList:
    classesInOrderTaken = list[Class]()
    levelOfClasses = dict[str, int]()
    subclassesTaken = dict[str, str]()
    subClassChoice = ""
    choice = None
    def __init__(self, startingClass: Class, character, isEmpty:bool=False) -> None:
        if(isEmpty):
            return
        self.levelOfClasses = {}
        self.classesInOrderTaken = []
        self.increaseClass(startingClass, character)

    def increaseClass(self, newClassLevel: Class, character) -> Choice:
        self.classesInOrderTaken.append(newClassLevel)
        level = self.levelOfClasses.get(newClassLevel.name, 0) 
        self.levelOfClasses[newClassLevel.name] = level + 1
        character.applyFeatures(newClassLevel.getFeaturesAtLevel(level, self.subclassesTaken.get(newClassLevel.name, None)))
        self.choice = newClassLevel.choicesAtLevel.get(level, None)

    def chooseSubclass(self, mainClass: Class, subclass: SubClass, character):
        self.subClassChoice = ""
        self.subclassesTaken[mainClass.name] = subclass.name
        levelWhenTaken = self.levelOfClasses[mainClass.name]-1
        character.applyFeatures(subclass.featuresAtLevel.get(levelWhenTaken, []))
    
    def getCopy(self):
        copyList = ClassList(None, None, True)
        copyList.levelOfClasses = self.levelOfClasses.copy()
        copyList.classesInOrderTaken = [*self.classesInOrderTaken]
        copyList.subclassesTaken = self.subclassesTaken.copy()
        if not (self.choice == None):
            copyList.choice = [*self.choice]
        copyList.subClassChoice = self.subClassChoice
        #assert copyList == self
        return copyList
    
    def __str__(self) -> str:
        return "\n  "+"\n  ".join([str(x[1])+" levels "+x[0]+(" ("+self.subclassesTaken[x[0]]+")" if not self.subclassesTaken.get(x[0], None) == None else "") for x in self.levelOfClasses.items()])
    
    def sameMainClass(self, b: Class) -> bool:
        if not isinstance(b, ClassList):
            return NotImplemented
        return  self.classesInOrderTaken == b.classesInOrderTaken and \
                self.levelOfClasses == b.levelOfClasses

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ClassList):
            return NotImplemented
        return  self.classesInOrderTaken == __value.classesInOrderTaken and \
                self.levelOfClasses == __value.levelOfClasses #and \
            #    self.subclassesTaken == self.subclassesTaken and \
             #   self.subClassChoice == self.subClassChoice