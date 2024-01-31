from Features import Feature
from Attributes import Attributes

class Race:
    def __init__(self, name: str, racialBonus: list[int], racialFeatures: list[Feature]) -> None:
        self.name = name
        self.racialBonus = racialBonus
        self.racialFeatures = racialFeatures

    def getStatBonus(self):
        return self.racialBonus
    
    def getRaceFeatures(self):
        return self.racialFeatures
    
    def __str__(self) -> str:
        return self.name + " [" + ", ".join(\
            [("+" if stat > 0 else "")+str(stat)+" "+Attributes.ATTRS_INV[i] for i, stat in enumerate(self.racialBonus) if not stat == 0])+"] " + \
            ("Features: "+", ".join([x.name for x in self.racialFeatures]) if len(self.racialFeatures) > 0 else "")