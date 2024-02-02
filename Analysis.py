from Mitosis import CombinationExplorer
from CharIO import getFeatures, getRaces, getWeapons, getActions, getFeats, getClasses

features = getFeatures()
races = getRaces(features)
weapons = getWeapons()
actions = getActions()
feats = getFeats(actions, features)
classes = getClasses(features)

if __name__ == "__main__":
    combi = CombinationExplorer(feats.values(), weapons.values(), races.values(), classes.values())
    combi.createCharactersLvl1(actions)