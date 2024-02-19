from enum import Enum

from .Requirements import Requireable, Requirement

class BonusType(Enum):
    onePerTurn = 'Once Per Turn'
    onePerHit = 'Every Attack'

class Source(Enum):
    dice = 0
    flat = 1
    table = 2

class BonusDamage(Requireable):
    requirements = list[Requirement]
    damage = dict()

    def __init__(self, bType: BonusType, requirements: list[Requirement], isWeaponDamage: bool, name: str, dice: list[(int, int)] = None, flat: int = None, table = None) -> None:
        from .Converter import Dice, Table
        assert table == None or type(table) == Table
        self.bType = bType
        self.name = name
        self.isWeaponDamage = isWeaponDamage
        self.requirements = requirements
        if not (dice == None):
            self.source = Source.dice
            self.damageDice = [0, 0]
            self.dice = dice
            damageBasic = Dice.averageValueForDice(dice)
            self.damageDice[0] = (damageBasic, damageBasic * 2)
            damageRerolls = Dice.averageValueForDiceWithRerolls(dice)
            self.damageDice[1] = (damageRerolls, damageRerolls * 2)

        elif not (flat == None):
            self.source = Source.flat
            self.damageFlat = flat

        elif not (table == None):
            self.source = Source.table
            self.tableOwner = table.ownerClass
            self.tableIsDice = table.dataType == "dice"
            self.tableName = table.tableName
            if(self.tableIsDice):
                self.damagePerLevel =  ([Dice.averageValueForDice(tableEntry) for tableEntry in table.entryPerLevel], \
                                        [Dice.averageValueForDiceWithRerolls(tableEntry) for tableEntry in table.entryPerLevel])
            else:
                self.damagePerLevel =  (table.entryPerLevel,\
                                        table.entryPerLevel)
                                        # Damage from Table at Level, gets rerolls only if character has appropiate feature AND the bonus is classified as weapon damage

    def parseBonusDamage(lines: list[str], name: str) -> 'BonusDamage':
        from .Converter import Converter
        bType = BonusType(lines.pop(0).split(": ")[1])
        isWeaponDamage = False
        dice = None
        flat = None
        table = None
        requirements = []
        for line in lines:
            words = line.split(" ")
            nType = words.pop(0)
            if(nType == "Req:"):
                requirements.append(Requirement(*words))
            elif(nType == "WeaponDamage:"):
                isWeaponDamage = words[0] == "True"
            elif(nType == "Damage:"):
                value = Converter.convert(words[1], words[0])
                if(words[1] == "table"):
                    table = value
                elif(words[1] == "int"):
                    flat = value
                else:
                    dice = value
        return BonusDamage(bType, requirements, isWeaponDamage, name, dice, flat, table)


    def getBonus(self, levelPerClass: dict[str, int], rerolls: bool): # returns normal and crit damage 
        if(self.source == Source.flat):
            return (self.damageFlat, self.damageFlat)
        if(self.source == Source.table):
            damage = self.damagePerLevel[rerolls and self.isWeaponDamage][levelPerClass[self.tableOwner]-1]
            return (damage, damage * (1 + self.tableIsDice))
        return self.damageDice[rerolls]

    def getImprovedStr(self, character) -> str: # As is, this is only called 5 times in analysis.py, so the import is fine and wont affect performance
        from .CharSheet import Character
        assert type(character) == Character
        return  self.bType.value +": "+\
                ("Average "+str(self.damagePerLevel[0][character.classes.levelOfClasses[self.tableOwner]-1])+" from "+self.tableName+" table" if self.source == Source.table else "")+\
                (", ".join([str(pair[0])+"d"+str(pair[1])+" from "+self.name for pair in self.dice]) if self.source == Source.dice else "")+\
                (str(self.damageFlat)+" from "+self.name if self.source == Source.flat else "")

    def __str__(self) -> str:
        return  self.bType.value +": "+\
                ("Damage from "+self.tableName+" table" if self.source == Source.table else "")+\
                (", ".join([str(pair[0])+"d"+str(pair[1])+" from "+self.name for pair in self.dice]) if self.source == Source.dice else "")+\
                (str(self.damageFlat)+" from "+self.name if self.source == Source.flat else "")

    def getRequirements(self) -> list[Requirement]:
        return self.requirements