from Requirements import Requireable, Requirement
from Features import Feature
from Attributes import Usefullness, AttributeType

class Class(Requireable):
    def __init__(self, name: str, lines: list[str], features: dict[str, Feature]) -> None:
        self.name = name
        self.requirement1 = None
        self.requirement2 = None
        self.reqType = None
        self.featuresAtLevel = dict[int, list[Feature]]()
        self.statUsefullness = dict[AttributeType, Usefullness]()
        for stat in AttributeType:
            self.statUsefullness[stat] = Usefullness.Okay
        subclasses = []
        currentSubClass = 0
        i = 0 # keep track what lines we've read
        for line in lines:
            if(line == "Type"):
                break # have now begun subclasses
            i += 1
            words = line.split(" ")
            if(words[0] == "Lvl:"):
                lvlNumber = int(words[1][:-1])
                featureNames = words[2].split("|")
                featureList = []
                for featureName in featureNames:
                    nameParts = featureName.split(">")
                    feature = features[nameParts[0]].getCopy()
                    if(len(nameParts) > 1):
                        feature.fillInValues(nameParts[1].split(":"))
                    featureList.append(feature)
                    assert feature.isFinished()
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
        self.preCalcUsefulls()

    def getFeaturesAtLevel(self, Level: int):
        return self.featuresAtLevel.get(Level, [])

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
            "\n".join(["    Level "+str(items[0]+1)+": "+",".join([feature.name for feature in items[1]]) for items in self.featuresAtLevel.items()])
                                                                              #+"["+", ".join([y+" "+feature.values[i] for i, y in enumerate(feature.effects)])+"]" 
    
from copy import deepcopy
class ClassList:
    classesInOrderTaken = list[Class]()
    levelOfClasses = dict[Class, int]()
    def __init__(self, startingClass: Class, character) -> None:
        self.levelOfClasses = {}
        self.classesInOrderTaken = []
        self.increaseClass(startingClass, character)

    def increaseClass(self, newClassLevel: Class, character):
        self.classesInOrderTaken.append(newClassLevel)
        level = self.levelOfClasses.get(newClassLevel, 0) 
        self.levelOfClasses[newClassLevel] = level + 1
        character.applyFeatures(newClassLevel.getFeaturesAtLevel(level))

    def getClassAtLevel(self, characterLevel: int) -> Class:
        return self.classesInOrderTaken[characterLevel]
    
    def getCopy(self):
        copyList = deepcopy(self)
        copyList.levelOfClasses = self.levelOfClasses.copy()
        copyList.classesInOrderTaken = self.classesInOrderTaken.copy()
        #for classTaken in self.classesInOrderTaken[1:]:
        #    copyList.increaseClass(classTaken, newChar)
        return copyList
    
    def __str__(self) -> str:
        return ", ".join([str(x[1])+" levels "+x[0].name for x in self.levelOfClasses.items()])
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ClassList):
            return NotImplemented
        return self.classesInOrderTaken == __value.classesInOrderTaken and self.levelOfClasses == __value.levelOfClasses