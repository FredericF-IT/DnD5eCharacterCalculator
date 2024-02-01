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
            effect = line.split(" ")
            effects.append(effect[0])
            if len(effect) == 2:
                values.append(effect[1])
        return (effects, values)
    
    def applyFeature(self, character):
        assert len(self.effects) == len(self.values)
        for i, effect in enumerate(self.effects):
            value = self.values[i]
            if("?" in effect):
                effect = effect.replace("?", value)
            variable = character.getVariable(effect)
            if(variable == None): 
                character.setVariable(effect, value)
                return
            
            value = type(variable)(value)
            
            character.setVariable(effect, variable + value)

    def supplyValues(self, values: list[str]):
        self.values = values                                            # TODO perhaps remove

    def getCopy(self):
        return Feature(self.name, self.effects.copy(), self.values.copy())

    def __str__(self) -> str:
        return self.name