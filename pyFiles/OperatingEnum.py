from enum import Enum
from os import name

class OperatingS(Enum):
    Windows = "nt"
    Linux = "posix"

def getSystem() -> 'OperatingS':
    return OperatingS(name)