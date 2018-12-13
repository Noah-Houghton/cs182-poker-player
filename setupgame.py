import fileinput
from pypokerengine.api.game import setup_config, start_poker
from fishbot import FishBot
import yaml
import sys, getopt

"""
Sample command to setup default game, no args
python setupgame.py

Sample command to set game with some args
python setupgame.py -a 5 -s 250 -r 5 -m 10 -p MonteCarloBot.py

Run game using
pypokergui serve poker_conf.yaml --port 8000 --speed moderate

"""


def main(argv):
    # default values
    a = 0
    b = None
    s = 100
    r = 10
    sb = 10
    pl = []
    setup = 'fishbot.py'
    numAgents = 2
    helpMessage = 'setupgame.py -a <ante> -b <blind_structure> -s <initial_stack> -r <max_round> -m <small_blind> -p <agentType>.py -n <numAgents>'
    try:
        opts, args = getopt.getopt(argv, "ha:b:s:r:m:p:n:", ["ante=", "blind_structure=", "initial_stack=", "max_round=", "small_blind=", "agentType=", "numAgents="])
    except getopt.GetoptError:
        print(helpMessage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(helpMessage)
            sys.exit()
        elif opt in ("-a", "--ante"):
            a = int(arg)
        elif opt in ("-b", "--blind_structure"):
            b = arg
        elif opt in ('-s', "--initial_stack"):
            s = int(arg)
        elif opt in ('-r', "--max_round"):
            r = int(arg)
        elif opt in ('-m', "--small_blind"):
            sb = int(arg)
        elif opt in ('-p', "--agentType"):
            setup = arg
        elif opt in ('-n', "--numAgents"):
            numAgents = int(arg)
        if setup [-3:] != ".py":
            setup += ".py"
    for i in range(numAgents):
        pl.append({"name": "Player {}".format(i), "path": setup.lower()})
    data = dict(
        ante = a,
        blind_structure = b,
        initial_stack = s,
        max_round = r,
        small_blind = sb,
        ai_players = pl,
    )
    with open("poker_conf.yaml", "w") as outfile:
        yaml.default_style =""
        yaml.dump(data, outfile, default_flow_style=False)
    print("config for game with {} {} created.".format(numAgents, setup[:-3]))

if __name__ == "__main__":
    main(sys.argv[1:])
