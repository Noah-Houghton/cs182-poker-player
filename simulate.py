from pypokerengine.api.game import start_poker, setup_config
import numpy as np
import sys, getopt, time
import importlib
# import agents

"""
Example command line to run with default config
python simulate.py -p MonteCarloBot -o FishBot -n 3 -g 10

Example command line to run with custom config
python simulate.py -p MonteCarloBot -o RandomBot -n 3 -g 10 -a 5 -s 500 -r 15 -m 15
"""

LOG_TEST = True


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
    nMoneyVictories = 0
    if not numTraining == 0:
        print("Beginning {} training games".format(numTraining))
        trainingTime = time.time()
    for round in range(numTraining):
        # run numTraining training games
        config = setup_config(max_round=conf["r"], initial_stack=conf["s"], small_blind_amount=conf["sb"], ante=conf["a"])
        CONFIG = config
        # + 1 for our agent
        for i in range(numAgents+1):
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
        print("Training complete!")
        trainingTime = time.time() - trainingTime
        for bot in bots:
            # forget record from training games
            bot.roundWins = 0
            bot.roundLosses = 0
    gameTime = time.time()
    print("Beginning {} games.".format(numGames))
    for round in range(numGames):
        config = setup_config(max_round=conf["r"], initial_stack=conf["s"], small_blind_amount=conf["sb"], ante=conf["a"])
        for i in range(len(bots)):
            config.register_player(name=("Player {}".format(i+1)), algorithm=bots[i])
        config.set_blind_structure(conf["b"])
        game_result = start_poker(config, verbose=0)
        # prints the average stack as the games advance
        stack_log.append([player['stack'] for player in game_result['players'] if player['uuid'] == agent.uuid])
        if round == numGames/4:
            print("simulation 25% complete")
        if round == numGames/2:
            print("simulation 50% complete")
        if round == numGames*3/4:
            print("simulation 75% complete")
        if round == numGames*9/10:
            print("simulation 90% complete")
        allStacks = [player['stack'] for player in game_result['players']]
        if max(allStacks) == stack_log[round][0]:
            nMoneyVictories += 1
    gameTime = time.time() - gameTime
    if not numTraining == 0:
        print("training time: {} seconds".format(trainingTime))
    # print(bots[0].qvalues)
    print("Average game time {} seconds".format(gameTime / float(numGames)))
    print("Avg. agent stack after {} games: {}".format(numGames, int(np.mean(stack_log))))
    print("Agent had most money {} games out of {}".format(nMoneyVictories, numGames) +" ({0:.0%})".format(nMoneyVictories/float(numGames)))
    print("Round win rate: {} out of {}".format(bots[0].roundWins, bots[0].roundWins + bots[0].roundLosses)+" ({0:.0%})".format(bots[0].roundWins/float(bots[0].roundWins + bots[0].roundLosses)))
    print("Finished simulating {} games with config:".format(numGames))
    print("Max round {}\nInitial stack {}\nSmall blind {}\nAnte {}\n{} {} opponents\nPlayer agent {}".format(conf["r"], conf["s"], conf["sb"], conf["a"], numAgents, conf["opponentType"], conf["agentType"]))
    print("Trained for {} games".format(numTraining))
    if LOG_TEST:
        # UPDATE THESE VALUES TO INCLUDE IN EXPORT
        try:
            alph = agent.alpha
            eps = agent.epsilon
            gamma = agent.discount
        except:
            alph = eps = gamma = None
        randomMMV = 1
        randomRVR = 1
        # CALCULATE RELATIONSHIPS
        if randomMMV is None or randomRVR is None or alph is None or eps is None or gamma is None:
            data = "{}".format(conf["agentType"])
            data += " & {0:.3f}".format(gameTime / float(numGames))
            data += " & {} & {}/{}".format(int(np.mean(stack_log)), nMoneyVictories, numGames)
            data += " ({0:.2%})".format(nMoneyVictories/float(numGames))
            data += " & {}/{}".format(bots[0].roundWins, bots[0].roundWins + bots[0].roundLosses)
            data += " ({0:.2%})".format(bots[0].roundWins/float(bots[0].roundWins + bots[0].roundLosses))
            data += " & - & - & - & -"
        else:
            MMVR = (nMoneyVictories/float(numGames)) / float(randomMMV)
            RVR = (bots[0].roundWins/float(bots[0].roundWins + bots[0].roundLosses)) / float(randomRVR)
            data = "{}".format(conf["agentType"])
            data += " & {0:.3f}".format(gameTime / float(numGames))
            data += " & {} & {}/{}".format(int(np.mean(stack_log)), nMoneyVictories, numGames)
            data += " ({0:.2%})".format(nMoneyVictories/float(numGames))
            data += " & {}/{}".format(bots[0].roundWins, bots[0].roundWins + bots[0].roundLosses)
            data += " ({0:.2%})".format(bots[0].roundWins/float(bots[0].roundWins + bots[0].roundLosses))
            data += " & {0:.2%} & {0:.2%}".format(MMVR, RVR)
            data += " & {} & $\\alpha={}$ $\\gamma={}$ $\\epsilon={}$".format(numTraining, alph, gamma, eps)
        data += "\\\\\\hline"
        data = data.replace("%", "\\%")
        with open("{}.txt".format(conf["agentType"]), "w+") as output:
            output.write(data)


if __name__ == '__main__':
    main(sys.argv[1:])
