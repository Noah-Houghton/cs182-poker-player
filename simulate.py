from pypokerengine.api.game import start_poker, setup_config
import numpy as np
import sys, getopt
import importlib
# import agents

"""
Example command line to run with default config
python simulate.py -p MonteCarloBot -o FishBot -n 3 -g 10

Example command line to run with custom config
python simulate.py -p MonteCarloBot -o RandomBot -n 3 -g 10 -a 5 -s 500 -r 15 -m 15
"""


def main(argv):
    # defaults for config
    a = 0
    b = {}
    s = 100
    r = 10
    sb = 10
    numTraining = 0
    helpMessage = 'simulate.py -p <agentType> -o <opponentType> -n <numOpponents> -g <numGames> -a <ante> -b <blind_structure> -s <initial_stack> -r <max_round> -m <small_blind> -t <numTraining>'
    try:
        opts, args = getopt.getopt(argv, "hp:n:g:o:a:b:s:r:m:t:", ["agentType=", "numOpponents=", "numGames=", "opponentType=", "ante=", "blind_structure=", "initial_stack=", "max_round=", "small_blind=", "numTraining="])
    except getopt.GetoptError:
        print(helpMessage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(helpMessage)
            sys.exit()
        elif opt in ("-p", "--agentType"):
            agentType = arg
        elif opt in ("-o", "--opponentType"):
            opponentType = arg
        elif opt in ('-n', "--numOpponents"):
            numAgents = int(arg)
        elif opt in ('-g', "--numGames"):
            numGames = int(arg)
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
        elif opt in ('-t', "--numTraining"):
            numTraining = int(arg)

    bots = []
    module = importlib.import_module('.'+agentType.lower(), package="bots")
    agent = module.setup_ai()
    # class_ = getattr(module, agentType)
    # agent = class_()
    bots.append(agent)
    for _ in range(numAgents):
        module = importlib.import_module('.'+opponentType.lower(), package="bots")
        opponent = module.setup_ai()
        # class_ = getattr(module, opponentType)
        bots.append(opponent)
    config = {"r":r, "a":a, "b":b, "s":s, "r":r, "sb":sb, "agentType":agentType, "opponentType":opponentType}
    runGames(bots, numAgents, numGames, agent, config, numTraining)

def runGames(bots, numAgents, numGames, agent, conf, numTraining):
    stack_log = []
    nVictories = 0
    if not numTraining == 0:
        print("Beginning {} training games".format(numTraining))
    for round in range(numTraining):
        # run numTraining training games
        config = setup_config(max_round=conf["r"], initial_stack=conf["s"], small_blind_amount=conf["sb"], ante=conf["a"])
        CONFIG = config
        for i in range(numAgents):
            config.register_player(name=("Player {}".format(i+1)), algorithm=bots[i])
        config.set_blind_structure(conf["b"])
        start_poker(config, verbose=0)
        if round == numTraining/4:
            print("25% trained")
        if round == numTraining/2:
            print("50% trained")
        if round == numTraining*3/4:
            print("75% trained")
        if round == numTraining*9/10:
            print("90% trained")
    if not numTraining == 0:
        print("Training complete! Beginning {} games.".format(numGames))
    for round in range(numGames):
        config = setup_config(max_round=conf["r"], initial_stack=conf["s"], small_blind_amount=conf["sb"], ante=conf["a"])
        for i in range(numAgents):
            config.register_player(name=("Player {}".format(i+1)), algorithm=bots[i])
        config.set_blind_structure(conf["b"])
        game_result = start_poker(config, verbose=0)
        # prints the average stack as the games advance
        stack_log.append([player['stack'] for player in game_result['players'] if player['uuid'] == agent.uuid])
        print("game {} complete".format(round+1))
        allStacks = [player['stack'] for player in game_result['players']]
        if max(allStacks) == stack_log[round][0]:
            nVictories += 1
    print("Avg. agent stack after {} games: {}".format(numGames, int(np.mean(stack_log))))
    print("Agent won {} games out of {} (%{})".format(nVictories, numGames, str(nVictories/float(numGames))[-2:]))
    print("Finished simulating {} games with config:".format(numGames))
    print("Max round {}\nInitial stack {}\nSmall blind {}\nAnte {}\n{} {} opponents\nPlayer agent {}".format(conf["r"], conf["s"], conf["sb"], conf["a"], numAgents, conf["opponentType"], conf["agentType"]))
    print("Trained for {} games".format(numTraining))

if __name__ == '__main__':
    main(sys.argv[1:])
