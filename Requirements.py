from Converter import Converter


class Requirement:
    def __init__(self, varPath: str, operator: str, value: str, typeName: str) -> None:
        self.varPath = varPath
        values = value.split("|")
        self.values = [Converter.convert(typeName, value) for value in values]
        self.operator = operator
        if(operator == "="):
            self.eval = self.equals
        elif(operator == ">"):
            self.eval = self.moreThen
        elif(operator == "<"):
            self.eval = self.lessThen

    def testRequirement(self, character):
        return self.eval(character)

    def equals(self, character) -> bool:
        variable = character.getVariable(self.varPath)
        values = self.values
        return any([variable == value for value in values])

    def lessThen(self, character) -> bool:
        variable = character.getVariable(self.varPath)
        values = self.values
        return any([variable < value for value in values])
    
    def moreThen(self, character) -> bool:
        variable = character.getVariable(self.varPath)
        values = self.values
        return any([variable > value for value in values])
    
    def __str__(self) -> str:
        return self.varPath + " " + self.operator + " " + " or ".join([str(value) for value in self.values])

class Requireable():
    def getRequirements(self) -> list[Requirement]: ...
    def isAvailable(self, character) -> bool: 
        available = True
        for req in self.getRequirements():
            print(req, req.testRequirement(character))
            available = available and req.testRequirement(character)
        return available