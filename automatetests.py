import subprocess
import simulate

"""
Populate "tests.txt" with the flags you want to run `python simulate.py` with.
Then run python `automatetests.py`.
"""

def main():
    testNum = 1
    with open("tests.txt", "r") as input:
        argslist = input.readlines()
    for args in argslist:
        print("Beginning test {}".format(testNum))
        simulate.main(args.split()+["-w"])
        testNum += 1

if __name__ == '__main__':
    main()
