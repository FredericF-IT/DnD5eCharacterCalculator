from .Features import Feature
from .Requirements import Requirement

class Choice():
    def __init__(self, name: str, featureChoices: list[tuple[Feature, Requirement]]) -> None:
        self.featureChoices = featureChoices
        self.name = name
        self.fullTitles = dict[str, str]()
        for feature in self.featureChoices:
            self.fullTitles[feature[0].name] = self.name+": "+feature[0].name

    def isAnAvailableOption(self, character, feature: tuple[Feature, Requirement]) -> bool: # Character will not be typed unless needed, as circular import occurs. For testing, uncomment:
        from .CharSheet import Character
        assert type(character) == Character
        return (feature[1] == None or feature[1].testRequirement(character)) and \
                not (self.fullTitles[feature[0].name] in character.gottenFeatures)

    def hasAvailableOptions(self, character) -> bool:
        return any([self.isAnAvailableOption(character, feature) for feature in self.featureChoices])

    def onePerChoice(self, character) -> list: # Character will not be typed unless needed, as circular import occurs. For testing, uncomment:
        from .CharSheet import Character
        assert type(character) == Character
        newCharacters = []
        for feature in self.featureChoices:
            if not (self.isAnAvailableOption(character, feature)):
                continue
            newCharacter = character.getCopy()
            newCharacter.applyFeatures([feature[0]])
            newCharacter.gottenFeatures.append(self.fullTitles[feature[0].name])
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
        return  self.name + "\n  " + \
                "\n  ".join([feature[0].name for feature in self.featureChoices])