from Feats import Feat
from Weapons import Weapon
from Races import Race
from CharSheet import Character


class CombinationExplorer:
    def __init__(self, feats: list[Feat], weapons: list[Weapon], races: list[Race]) -> None:
        self.feats = feats
        self.weapons = weapons
        self.races = races
    
    def createCharactersLvl1() -> list[Character]:
        pass