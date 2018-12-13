from pypokerengine.api.game import start_poker, setup_config
import numpy as np
import sys, getopt
import importlib
# import agents



def main(argv):
    helpMessage = 'simulate.py -a <agentType> -o <opponentType> -n <numOpponents> -g <numGames>'
    try:
        opts, args = getopt.getopt(argv, "ha:n:g:o:", ["agentType=", "numOpponents=", "numGames=", "opponentType="])
    except getopt.GetoptError:
        print(helpMessage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(helpMessage)
            sys.exit()
        elif opt in ("-a", "--agentType"):
            agentType = arg
        elif opt in ("-o", "--opponentType"):
            opponentType = arg
        elif opt in ('-n', "--numOpponents"):
            numAgents = int(arg)
        elif opt in ('-g', "--numGames"):
            numGames = int(arg)

    bots = []
    module = importlib.import_module(agentType.lower())
    agent = module.setup_ai()
    # class_ = getattr(module, agentType)
    # agent = class_()
    bots.append(agent)
    for _ in range(numAgents):
        module = importlib.import_module(opponentType.lower())
        opponent = module.setup_ai()
        # class_ = getattr(module, opponentType)
        bots.append(opponent)
    runGames(bots, numAgents, numGames, agent)

def runGames(bots, numAgents, numGames, agent):
    stack_log = []
    for round in range(numGames):
        config = setup_config(max_round=5, initial_stack=100, small_blind_amount=5)
        for i in range(numAgents):
            config.register_player(name=("Player {}".format(i+1)), algorithm=bots[i])
        game_result = start_poker(config, verbose=0)
        # prints the average stack as the games advance
        stack_log.append([player['stack'] for player in game_result['players'] if player['uuid'] == agent.uuid])
        print("Avg. agent stack as of game {}: {}".format(round+1, int(np.mean(stack_log))))

if __name__ == '__main__':
    main(sys.argv[1:])
