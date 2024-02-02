from Attributes import AttributeType
from Weapons import Dice

class Converter:
    getType = {
        'str': str,
        'int': int,
        'bool': bool,
        'attrTpye' : AttributeType,
        'dice': Dice
    }

    def convert(typeName: str, valueStr: str) -> None:
        if(typeName == 'dice'):
            return Dice.parseDice(valueStr)
        return (Converter.getType[typeName])(valueStr)