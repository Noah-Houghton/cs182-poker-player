import util
# import layout
import sys, types, time, random, os
from rules import ClassicGameRules

#############################
# FRAMEWORK TO START A GAME #
#############################

def default(str):
    return str + ' [Default: %default]'

def parseAgentArgs(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key,val = p, 1
        opts[key] = val
    return opts

def readCommand( argv ):
    """
    Processes the command used to run fivecard hold'em from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python fivecard-holdem.py <options>
    EXAMPLES:   (1) python fivecard-holdem.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-p', '--player', dest='player',
                      help=default('the agent TYPE in the agents module to use'),
                      metavar='TYPE', default='ReflexAgent')
    # parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
    #                   help='Display output as text only', default=False)
    # parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
    #                   help='Generate minimal output and no graphics', default=True)
    parser.add_option('-g', '--opponents', dest='opponent',
                      help=default('the opponent agent TYPE in the agents module to use'),
                      metavar = 'TYPE', default='RandomOpponent')
    parser.add_option('-k', '--numopponents', type='int', dest='numOpponents',
                      help=default('The maximum number of opponents to use'), default=3)
    # parser.add_option('-z', '--zoom', type='float', dest='zoom',
    #                   help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('--replay', dest='gameToReplay',
                      help='A recorded game file (pickle) to replay', default=None)
    parser.add_option('-a','--agentArgs',dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    parser.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)
    parser.add_option('-s', '--suppressOutput', action='store_true', dest='suppressOutput', help='Prevents games from printing',
                      default=False)
    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed: random.seed('cs188')

    # Choose a layout
    # args['layout'] = layout.getLayout( options.layout )
    # if args['layout'] == None: raise Exception("The layout " + options.layout + " cannot be found")

    # Choose a Pacman agent
    # noKeyboard = options.gameToReplay == None and (options.textGraphics or options.quietGraphics)
    playerType = loadAgent(options.player)
    agentOpts = parseAgentArgs(options.agentArgs)
    if options.numTraining > 0:
        args['numTraining'] = options.numTraining
        if 'numTraining' not in agentOpts: agentOpts['numTraining'] = options.numTraining
    player = playerType(**agentOpts) # Instantiate Pacman with agentArgs
    args['player'] = player

    # Don't display training games
    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    # Choose a ghost agent
    opponentType = loadAgent(options.opponent)
    args['opponents'] = [opponentType( i+1 ) for i in range( options.numOpponents )]

    # Choose a display format
    # if options.quietGraphics:
    #     import textDisplay
    #     args['display'] = textDisplay.NullGraphics()
    # elif options.textGraphics:
    #     import textDisplay
    #     textDisplay.SLEEP_TIME = options.frameTime
    #     args['display'] = textDisplay.PokerGraphics()
    # else:
    #     import graphicsDisplay
    #     args['display'] = graphicsDisplay.PacmanGraphics(options.zoom, frameTime = options.frameTime)
    args['suppressPrint'] = options.suppressOutput
    args['numGames'] = options.numGames
    args['record'] = options.record
    args['catchExceptions'] = options.catchExceptions
    args['timeout'] = options.timeout

    # Special case: recorded games don't use the runGames method or args structure
    if options.gameToReplay != None:
        print 'Replaying recorded game %s.' % options.gameToReplay
        import cPickle
        f = open(options.gameToReplay)
        try: recorded = cPickle.load(f)
        finally: f.close()
        # recorded['display'] = args['display']
        replayGame(**recorded)
        sys.exit(0)

    return args

def loadAgent(opponent):
    # Looks through all pythonPath Directories for the right module,
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir): continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except:
                print("import error")
                continue
            if opponent in dir(module):
                # if nographics and modulename == 'keyboardAgents.py':
                #     raise Exception('Using the keyboard requires graphics (not text display)')
                return getattr(module, opponent)
    raise Exception('The agent ' + opponent + ' is not specified in any *Agents.py.')

# def replayGame( layout, actions, display ):
#     import pacmanAgents, ghostAgents
#     rules = ClassicGameRules()
#     agents = [playerAgents.GreedyAgent()] + [opponentAgents.RandomOpponent(i+1) for i in range(layout.getNumOpponents())]
#     game = rules.newGame( layout, agents[0], agents[1:], display )
#     state = game.state
#     display.initialize(state.data)
#
#     for action in actions:
#             # Execute the action
#         state = state.generateSuccessor( *action )
#         # Change the display
#         display.update( state.data )
#         # Allow for game specific conditions (winning, losing, etc.)
#         rules.process(state, game)
#
#     display.finish()

def runGames( player, opponents, numGames, record, numTraining = 0, catchExceptions=False, timeout=30, suppressPrint=False ):
    import __main__
    # __main__.__dict__['_display'] = display

    import time
    rules = ClassicGameRules(timeout)
    games = []
    gamesTime = []
    firstTime = time.time()
    for i in range( numGames ):
        beQuiet = i < numTraining
        if beQuiet:
                # Suppress output and graphics
            # import textDisplay
            # gameDisplay = textDisplay.NullGraphics()
            rules.quiet = True
        else:
            # gameDisplay = display
            rules.quiet = False
        if not beQuiet:
            if i == numGames / 4:
                print("1/4 done! Time {}".format(time.time() - firstTime))
            if i == numGames / 2:
                print("halfway done! Time {}".format(time.time() - firstTime))
            if i == (numGames / 4) * 3:
                print("3/4 done! Time {}".format(time.time() - firstTime))
        game = rules.newGame(player, opponents, beQuiet, catchExceptions, suppressPrint)
        # start timer
        startTime = time.time()
        game.run()
        # end timer when game has ended
        gamesTime.append(time.time() - startTime)
        if not beQuiet: games.append(game)

        if record:
            import time, cPickle
            fname = ('recorded-game-%d' % (i + 1)) +  '-'.join([str(t) for t in time.localtime()[1:6]])
            f = file(fname, 'w')
            components = {'layout': layout, 'actions': game.moveHistory}
            cPickle.dump(components, f)
            f.close()

    if (numGames-numTraining) > 0:
        scores = [game.state.getScore() for game in games]
        wins = [game.state.isWin() for game in games]
        winRate = wins.count(True)/ float(len(wins))
        print 'Total Time:', time.time() - firstTime
        print 'Average Time:', sum(gamesTime) / float(len(gamesTime))
        print 'Average Score:', sum(scores) / float(len(scores))
        print 'Scores:       ', ', '.join([str(score) for score in scores])
        print 'Win Rate:      %d/%d (%.2f)' % (wins.count(True), len(wins), winRate)
        print 'Record:       ', ', '.join([ ['Loss', 'Win'][int(w)] for w in wins])

    return games

if __name__ == '__main__':
    """
    The main function called when pacman.py is run
    from the command line:

    > python fivecard-holdem.py

    See the usage string for more details.

    > python fivecard-holdem.py --help
    """
    args = readCommand( sys.argv[1:] ) # Get game components based on input
    runGames( **args )
    # import cProfile
    # cProfile.run("runGames( **args )")
    pass
