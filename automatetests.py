import subprocess
import simulate

"""
Populate "tests.txt" with the flags you want to run `python simulate.py` with.
Then run python `automatetests.py`.

Example format for `tests.txt`:
-p SarsaBot -o NaiveBot -n 1 -g 10 -a 5 -s 500 -r 50 -m 15 -t 10

Note that running automatetests.py will APPEND the output of the tests to the existing files.
Make sure to delete any tests you don't want to re-run from `tests.txt` before launching the program, or delete
them in `XXXbot.txt` to prevent logging the data twice!

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
