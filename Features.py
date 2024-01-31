#from CharSheet import Character
# Undo comment to see variables from character here, but dont keep during compile, as it results in a circular reference

class Feature:
    effects = []
    values = []
    def __init__(self, name: str, effects: list[str], values: list[str]) -> None:
        self.name = name
        self.values = values
        self.effects = effects

    def parseEffectsValues(lines: list[str]) -> (str, str):
        effects, values = [], []
        for line in lines:
            effect = line.rstrip().split(" ")
            effects.append(effect[0])
            if len(effect) == 2:
                values.append(effect[1])
        return (effects, values)

    def supplyValues(self, values: list[str]):
        self.values = values                                            # TODO split values

    def getCopy(self):
        return Feature(self.name, self.effects, self.values)

    def applyFeatures(self, character):
        assert len(self.effects) == len(self.values)
        for i, effect in enumerate(self.effects):
            variable = character.getVariable(effect)
            value = self.values[i]
            if(type(variable) is int):
                value = int(value)
            character.setVariable(effect, variable + value)

    def __str__(self) -> str:
        return self.name