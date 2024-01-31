from CharSheet import Character

getType = {
    'str': str,
    'int': int
}

class Requirement:
    def __init__(self, varPath: str, operator: str, value: str, typeName: str) -> None:
        self.varPath = varPath
        converter = getType[typeName]
        values = value.split("|")
        self.values = [converter(value) for value in values]
        self.operator = operator
        if(operator == "="):
            self.eval = self.equals
        elif(operator == ">"):
            self.eval = self.moreThen
        elif(operator == "<"):
            self.eval = self.lessThen

    def testRequirement(self, character: Character):
        return self.eval(character)

    def equals(self, character: Character) -> bool:
        variable = character.getVariable(self.varPath)
        values = self.values
        return any([variable == value for value in values])

    def lessThen(self, character: Character) -> bool:
        variable = character.getVariable(self.varPath)
        values = self.values
        return any([variable < value for value in values])
    
    def moreThen(self, character: Character) -> bool:
        variable = character.getVariable(self.varPath)
        values = self.values
        return any([variable > value for value in values])
    
    def __str__(self) -> str:
        return self.varPath + " " + self.operator + " " + " or ".join(self.values)

class Requireable():
    def getRequirements(self) -> list[Requirement]: ...
    def isAvailable(self, character: Character) -> bool: 
        available = True
        for req in self.getRequirements():
            available = available and req.testRequirement(character)
        return available