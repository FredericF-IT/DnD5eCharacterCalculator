from .Requirements import Requirement, Requireable
from .Actions import Action
from .Features import Feature
from .CharSheet import Character
from .Choices import Choice

class Feat(Requireable):
    def __init__(self, name: str, lines: list[str], actions: dict[str, Action], features: dict[str, Feature], choiceDict: dict[str, Choice]) -> None:
        self.name = name
        self.requirements = list[Requirement]()
        self.actions = set[Action]()
        self.features = list[Feature]()
        self.choices = list[Choice]()
        for line in lines:
            words = line.split(" ")
            identifier = words.pop(0)
            if(identifier == "Req:"):
                self.requirements.append(Requirement(*words))
            elif(identifier == "Action:"):
                self.actions.add(actions[words[0]])
            elif(identifier == "Feature:"):
                feature = features[words[0]].getCopy()
                self.features.append(feature)
            elif(identifier == "Choice:"):
                choice = choiceDict[words[0]]
                self.choices.append(choice)
    
    def applyToCharacter(self, character: Character):
        character.applyFeatures(self.features)
        character.gottenFeatures.append(self.name)
        character.actions = character.actions.union(self.actions)
        character.classes.addChoice(self.choices)

    def __str__(self) -> str:
        return self.name + \
            ("\n" if len(self.requirements) > 0 else "") + "\n".join(["  If "+str(req) for req in self.requirements]) + \
            ("\n  Actions: " if len(self.actions) > 0 else "") + ", ".join([action.name for action in self.actions]) + \
            ("\n  Choices:\n    " if len(self.choices) > 0 else "") + "\n    ".join([str(choice) for choice in self.choices]).replace("\n", "\n    ") + \
            ("\n  Features: " if len(self.features) > 0 else "") + ", ".join([action.name for action in self.features])

    def getRequirements(self) -> list[Requirement]:
        return self.requirements
    
    def isAvailable(self, character) -> bool:
        return super().isAvailable(character) and all([choice.hasAvailableOptions(character) for choice in self.choices])