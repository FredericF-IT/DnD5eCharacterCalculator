from Features import Feature
from Attributes import AttributeType, Attributes

class Race:
    def __init__(self, name: str, racialBonus: dict[AttributeType, int], racialFeatures: list[Feature]) -> None:
        self.name = name
        self.racialBonus = racialBonus
        self.racialFeatures = racialFeatures

    def getStatBonus(self):
        return self.racialBonus
    
    def getRaceFeatures(self):
        return self.racialFeatures
    
    def parseRace(lines: list[str], races: dict, allFeatures: dict[str, Feature]):
        i = 2
        subracesLeft = True
        while(subracesLeft):
            name = lines[i-1]
            stats = Attributes.makeDict(AttributeType, [0,0,0,0,0,0])
            features = []
            if(len(lines) > i+1 and lines[i+1] == "Stats"):
                i += 2
                line = lines[i]
                while(line != "-----------"):
                    attr, value = line.split(" ")

                    if(attr == "All"):
                        for key in stats.keys():
                            stats[key] = stats[key] + 1
                    else:
                        stats[AttributeType(attr)] = int(value)
                    i += 1
                    line = lines[i]
            if(len(lines) > i+1 and lines[i+1] == "Features"):
                i += 2
                line = lines[i]
                while(line != "-----------"):
                    featureInfo = line.split(" ")
                    feature = allFeatures[featureInfo[0]].getCopy()
                    if(not len(featureInfo) == 1):
                        feature.supplyValues(featureInfo[1:])
                    features.append(feature)
                    i += 1
                    line = lines[i]
            subracesLeft = len(lines) > i+3 and lines[i+2] == "Type"
            i += 4
            races[name] = Race(name, stats, features)
    
    def __str__(self) -> str:
        return self.name + " [" + ", ".join(\
            [("+" if self.racialBonus[stat] > 0 else "")+str(self.racialBonus[stat])+" "+stat.name for stat in self.racialBonus.keys() if not stat == 0])+"] " + \
            ("Features: "+", ".join([x.name for x in self.racialFeatures]) if len(self.racialFeatures) > 0 else "")