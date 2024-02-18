from .Converter import Converter


class Requirement:
    def __init__(self, varPath: str, operator: str, value: str, typeName: str) -> None:
        self.getInfoFromMethod = "(" in varPath
        (variable, methodCall, unused, unused, unused) = Converter.parsePaths([(varPath if self.getInfoFromMethod else varPath.replace("]", " ? ?]"))], None, None)
        if(self.getInfoFromMethod):
            self.info = methodCall[0]
        else:
            self.info = variable[0]

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
    
    def getCompareValue(self, character):
        if(self.getInfoFromMethod):
            return character.useMethod(self.info[0], self.info[1])
        return character.getVariable(self.info[0])

    def equals(self, character) -> bool:
        variable = self.getCompareValue(character)
        values = self.values
        return any([variable == value for value in values])

    def lessThen(self, character) -> bool:
        variable = self.getCompareValue(character)
        values = self.values
        return any([variable < value for value in values])
    
    def moreThen(self, character) -> bool:
        variable = self.getCompareValue(character)
        values = self.values
        return any([variable > value for value in values])
    
    def __str__(self) -> str:
        return self.info[0] + \
            " " + self.operator + " " + \
            " or ".join([str(value) for value in self.values])

class Requireable():
    def getRequirements(self) -> list[Requirement]: ...
    def isAvailable(self, character) -> bool: 
        available = True
        for req in self.getRequirements():
            available = available and req.testRequirement(character)
        return available