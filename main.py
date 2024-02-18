from pyFiles.Analysis import analyzeClasses
from pyFiles.Creator import createCharacter

def printHelp():
    print("You can type:\n"\
          + "  A number to choose what function to use\n"\
          + "You can also type:\n"\
          + "  Help        - to see this text\n"\
          + "  Stop / Exit - Either closes the program\n")

if __name__ == "__main__":
    createCharacter()

    assert False

    keepGoing = True
    while(keepGoing):
        choice = input("What would you like to do?\n\
                      1. Analyze all possible Characters\n\
                      2. Create specific Character\n\
                      3. Help (commands)\n")
        levelNorm = choice.lower().lstrip().rstrip()
        if(levelNorm in ["exit", "stop"]):
            break
        elif(levelNorm == "help"):
            printHelp()
            #print("Swap - to use different ranking mode") NOTE not implemented
        else:
            try:
                choice = int(choice)
            except:
                print("Unrecognized input: "+str(choice))
                continue
            if(choice < 1 or choice > 3):
                print("Number"+str(choice)+" not in range, please try again.\n")
            else:
                #rankBuildsFinally(level, characterSelection.BestOverall)
                if(choice == 1):
                    analyzeClasses()
                elif(choice == 2):
                    createCharacter()
                elif(choice == 3):
                    printHelp()
        print("\n\n")