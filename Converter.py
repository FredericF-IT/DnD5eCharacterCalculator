from Attributes import AttributeType

class Converter:
    getType = {
        'str': str,
        'int': int,
        'attrTpye' : AttributeType,
    }

    def convert(typeName: str, valueStr: str) -> None:
        return (Converter.getType[typeName])(valueStr)