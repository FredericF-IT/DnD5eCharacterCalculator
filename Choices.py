from Features import Feature
from Requirements import Requirement

class Choice():
    def __init__(self, name: str, featureChoices: list[(Feature, Requirement)]) -> None:
        self.featureChoices = featureChoices
        self.name = name

    def onePerChoice(self, character) -> list:
        newCharacters = []
        for feature in self.featureChoices:
            if not (feature[1] == None or feature[1].testRequirement(character)):
                continue
            fullTitle = self.name+": "+feature[0].name
            if(fullTitle in character.gottenFeatures):
                continue
            newCharacter = character.getCopy()
            newCharacter.applyFeatures([feature[0]])
            newCharacter.gottenFeatures.append(fullTitle)
            newCharacters.append(newCharacter)
        return newCharacters

    def parseChoice(name: str, lines: list[str], features: dict[str, Feature]) -> 'Choice':
        choices = []
        for line in lines:
            featureParts = line.split(" ")
            if(len(featureParts) == 1):
                choices.append((features[featureParts[0]], None))
                continue
            featureName = featureParts[0]
            requirment = Requirement(featureParts[2], featureParts[3], featureParts[4], featureParts[5])
            choices.append((features[featureName], requirment))
        return Choice(name, choices)
    
    def __str__(self) -> str:
        return  self.name + "\n" + \
                "\n".join([str(feature[0]) for feature in self.featureChoices])