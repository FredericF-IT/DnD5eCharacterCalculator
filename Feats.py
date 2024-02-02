from Requirements import Requirement, Requireable
from Actions import Action
from Features import Feature
from CharSheet import Character

class Feat(Requireable):
    def __init__(self, name: str, lines: list[str], actions: dict[str, Action], features: dict[str, Feature]) -> None:
        self.name = name
        self.requirements = list[Requirement]()
        self.actions = set[Action]()
        self.features = []
        for line in lines:
            words = line.split(" ")
            if(words[0] == "Req:"):
                self.requirements.append(Requirement(words[1], words[2], words[3], words[4]))
            elif(words[0] == "Action:"):
                self.actions.add(actions[words[1]])
            elif(words[0] == "Feature:"):
                feature = features[words[1]].getCopy()
                self.features.append(feature)
    
    def applyToCharacter(self, character: Character):
        character.applyFeatures(self.features, True)
        character.actions.union(self.actions)

    def __str__(self) -> str:
        return self.name + \
            ("\n" if len(self.requirements) > 0 else "") + "\n".join(["  If "+str(req) for req in self.requirements]) + \
            ("\n  Actions: " if len(self.actions) > 0 else "") + ", ".join([action.name for action in self.actions]) + \
            ("\n  Features: " if len(self.features) > 0 else "") + ", ".join([action.name for action in self.features])

    def getRequirements(self) -> list[Requirement]:
        return self.requirements