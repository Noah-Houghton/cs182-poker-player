from pypokerengine.api.game import start_poker, setup_config
import numpy as np
import sys, getopt, time
import importlib

"""
Example command line to run with default config
python simulate.py -p MonteCarloBot -o FishBot -n 3 -g 10

Example command line to run with custom config
python simulate.py -p MonteCarloBot -o RandomBot -n 3 -g 10 -a 5 -s 500 -r 15 -m 15
"""

# PRINTQVALUES = True
PRINTQVALUES = False

# PRINTRESULT = True
PRINTRESULT = False

def consoleLog(str):
    if PRINTRESULT:
        print(str)

def QLog(str):
    if PRINTQVALUES:
        print(str)

def main(argv):
    # defaults for config
    a = 0
    b = {}
    s = 100
    r = 10
    sb = 4
    log = False
    numTraining = 0
    numAgents = 1
    numGames = 1

    helpMessage = 'simulate.py -p <agentType> -o <opponentType> -n <numOpponents> -g <numGames> -a <ante> -b <blind_structure> -s <initial_stack> -r <max_round> -m <small_blind> -t <numTraining> -w <writeToLog> -l <alpha> -e <epsilon> -d <discount>'
    try:
        opts, args = getopt.getopt(argv, "hp:n:g:o:a:b:s:r:m:t:wl:e:d:", ["agentType=", "numOpponents=", "numGames=", "opponentType=", "ante=", "blind_structure=", "initial_stack=", "max_round=", "small_blind=", "numTraining=", "writeToLog=", "alpha=", "epsilon=", "discount="])
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
        elif opt in ('-w', "--writeToLog"):
            log = True
        elif opt in ('-l', "--alpha"):
            alpha = float(arg)
        elif opt in ('-e', '--epsilon'):
            epsilon = float(arg)
        elif opt in ('-d', '--discount'):
            discount = float(arg)


    bots = []
    module = importlib.import_module('.'+agentType.lower(), package="bots")
    agent = module.setup_ai()
    # class_ = getattr(module, agentType)
    # agent = class_()
    bots.append(agent)
    try:
        agent.alpha = alpha
    except:
        pass
    try:
        agent.epsilon = epsilon
    except:
        pass
    try:
        agent.discount = discount
    except:
        pass
    for _ in range(numAgents):
        module = importlib.import_module('.'+opponentType.lower(), package="bots")
        opponent = module.setup_ai()
        # class_ = getattr(module, opponentType)
        bots.append(opponent)
    config = {"r":r, "a":a, "b":b, "s":s, "r":r, "sb":sb, "agentType":agentType, "opponentType":opponentType}
    runGames(bots, numAgents, numGames, agent, config, numTraining, log)

def runGames(bots, numAgents, numGames, agent, conf, numTraining, log):
    stack_log = []
    nMoneyVictories = 0
    if not numTraining == 0:
        consoleLog("Beginning {} training games".format(numTraining))
        trainingTime = time.time()
    try:
        agent.doUpdate = True
    except:
        pass
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
            consoleLog("25% trained")
        if round == numTraining/2:
            consoleLog("50% trained")
        if round == numTraining*3/4:
            consoleLog("75% trained")
        if round == numTraining*9/10:
<<<<<<< HEAD
            print("90% trained")
    try:   
        agent.doUpdate = False
    except:
        pass
=======
            consoleLog("90% trained")
>>>>>>> bbb5e721a500646a042afa360cc4ab00395332b6
    if not numTraining == 0:
        consoleLog("Training complete!")
        trainingTime = time.time() - trainingTime
        for bot in bots:
            # forget record from training games
            bot.roundWins = 0
            bot.roundLosses = 0
    gameTime = time.time()
    consoleLog("Beginning {} games.".format(numGames))
    for round in range(numGames):
        config = setup_config(max_round=conf["r"], initial_stack=conf["s"], small_blind_amount=conf["sb"], ante=conf["a"])
        for i in range(len(bots)):
            config.register_player(name=("Player {}".format(i+1)), algorithm=bots[i])
        config.set_blind_structure(conf["b"])
        game_result = start_poker(config, verbose=0)
        # prints the average stack as the games advance
        stack_log.append([player['stack'] for player in game_result['players'] if player['uuid'] == agent.uuid])
        if round == numGames/4:
            consoleLog("simulation 25% complete")
        if round == numGames/2:
            consoleLog("simulation 50% complete")
        if round == numGames*3/4:
            consoleLog("simulation 75% complete")
        if round == numGames*9/10:
            consoleLog("simulation 90% complete")
        allStacks = [player['stack'] for player in game_result['players']]
        if max(allStacks) == stack_log[round][0]:
            nMoneyVictories += 1
    gameTime = time.time() - gameTime
    if not numTraining == 0:
        consoleLog("training time: {} seconds".format(trainingTime))
    # print(bots[0].qvalues)
    consoleLog("Average game time {} seconds".format(gameTime / float(numGames)))
    consoleLog("Avg. agent stack after {} games: {} vs start @ {}".format(numGames, int(np.mean(stack_log)), conf["s"]))
    consoleLog("Agent had most money {} games out of {}".format(nMoneyVictories, numGames) +" ({0:.0%})".format(nMoneyVictories/float(numGames)))
    consoleLog("Round win rate: {} out of {}".format(bots[0].roundWins, bots[0].roundWins + bots[0].roundLosses)+" ({0:.0%})".format(bots[0].roundWins/float(bots[0].roundWins + bots[0].roundLosses)))
    consoleLog("Finished simulating {} games with config:".format(numGames))
    consoleLog("Max round {}\nInitial stack {}\nSmall blind {}\nAnte {}\n{} {} opponents\nPlayer agent {}".format(conf["r"], conf["s"], conf["sb"], conf["a"], numAgents, conf["opponentType"], conf["agentType"]))
    try:
        consoleLog("Hyperparams: A = {}, G = {}, E = {}".format(agent.alpha, agent.discount, agent.epsilon))
    except:
        pass
    consoleLog("Trained for {} games".format(numTraining))
    try:
        QLog("agent qvals {}".format(agent.qvalues))
    except:
        pass
    if log:
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
            data += " & {} vs {} @start & {}/{}".format(int(np.mean(stack_log)),conf["s"], nMoneyVictories, numGames)
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
        with open("{}.txt".format(conf["agentType"]), "a+") as output:
            output.write(data+"\n")

        configuration = "Ante: {} Small Blind: {} Initial Stack: {} Max Round: {} Number Opponents: {} Opponent Type: {}\n".format(conf["a"], conf["sb"], conf["s"], conf["r"], numAgents, conf["opponentType"])
        with open("{}_configs.txt".format(conf["agentType"]), "a+") as output:
            output.write(configuration)


if __name__ == '__main__':
    main(sys.argv[1:])
