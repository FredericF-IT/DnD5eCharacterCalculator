from Requirements import Requireable, Requirement
from Features import Feature

class Class(Requireable):
    def __init__(self, name: str, lines: list[str], features: dict[str, Feature]) -> None:
        self.name = name
        self.requirements = []
        self.featuresAtLevel = dict[int, list[Feature]]()
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
                        feature.supplyValues([nameParts[1]])
                    featureList.append(feature)
                self.featuresAtLevel[lvlNumber-1] = featureList
            elif(words[0] == "Req:"):
                self.requirements.append(Requirement(words[1], words[2], words[3], words[4]))
        
        # TODO Subclasses

    def getFeaturesAtLevel(self, Level: int):
        return self.featuresAtLevel.get(Level, [])

    def getRequirements(self) -> list[Requirement]:
        return self.requirements
    
    def __str__(self) -> str:
        return self.name + \
            "\n  If "+" and ".join([str(req) for req in self.requirements]) + "\n  Features:" + "\n" + \
            "\n".join(["    Level "+str(items[0]+1)+": "+",".join([feature.name+"["+", ".join([y+" "+feature.values[i] for i, y in enumerate(feature.effects)])+"]" for feature in items[1]]) for items in self.featuresAtLevel.items()])

class ClassList:
    classesInOrderTaken = list[Class]()
    levelOfClasses = dict[Class, int]()
    def __init__(self, startingClass: Class, character) -> None:
        self.increaseClass(startingClass, character)

    def increaseClass(self, newClassLevel: Class, character):
        self.classesInOrderTaken.append(newClassLevel)
        level = self.levelOfClasses.get(newClassLevel, 0) 
        self.levelOfClasses[newClassLevel] = level + 1
        character.applyFeatures(newClassLevel.getFeaturesAtLevel(level))

    def getClassAtLevel(self, characterLevel: int):
        return self.classesInOrderTaken[characterLevel]
    
    def __str__(self) -> str:
        return ", ".join([str(x[1])+" levels "+x[0].name for x in self.levelOfClasses.items()])