import util
import agents
import random


"""
Common set of functions for rules
"""
class Rules:

    def newGame( self, playerAgent, opponentAgents, quiet = False, catchExceptions=False):
        # agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        agents = [playerAgent] + opponentAgents
        initState = GameState()
        initState.initialize(len(agents) - 1)
        game = Game(agents, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return game

    def process(self, state, game):
        """
        Checks to see whether it is time to end the current phase of the game.
        """
        if state.isWin(): self.win(state, game)
        if state.isLose(): self.lose(state, game)
    #     if state.isRoundEnd(): self.roundEnd(state, game)
    #     if state.isHandEnd(): self.handEnd(state, game)
    #
    # def roundEnd(self, state, game):
    #     game.roundComplete = True
    #
    # def handEnd(self, state, game):
    #     game.handComplete = True

    def win( self, state, game ):
        # if not self.quiet: print "Pacman emerges victorious! Score: %d" % state.data.score
        game.gameOver = True

    def lose( self, state, game ):
        # if not self.quiet: print "Pacman died! Score: %d" % state.data.score
        game.gameOver = True


"""
Defines a set of rules by which the player operates
"""
class PlayerRules(Rules):

    def getLegalActions(self):
        pass
    getLegalActions = staticmethod( getLegalActions )

    def applyAction(self, state, action):
        pass
    applyAction = staticmethod( applyAction )

"""
Defines a set of rules by which the opponents operate
"""
class OpponentRules(Rules):
    def getLegalActions(self, agentIndex):
        pass
    getLegalActions = staticmethod( getLegalActions )

    def applyAction(self, state, action, agentIndex):
        pass
    applyAction = staticmethod( applyAction )


class Actions:
    CL = "Call"
    FLD = "Fold"
    RS = "Raise"
    DD = "Double Down"
    AI = "All-In"

def Suite(shorthand):
        if shorthand == "H":
            return "Hearts"
        elif shorthand == "D":
            return "Diamonds"
        elif shorthand == "C":
            return "Clubs"
        elif shorthand == "S":
            return "Spades"

def Card(value, suite):
    """
    Given a value [1, 13] and a suite [H, D, C, S]
    returns a tuple of (value, suite)
    """
    return (value, Suite(suite))

def selectSuite(lst, suite):
    cards = [card for card in lst if card[1] == suite]
    cards.sort()
    return cards

def selectValue(lst, num):
    cards = [card for card in lst if card[0] == num]
    cards.sort()
    return cards

class Deck:
    cards = []
    # use this to reshuffle deck so that cards the players already have are not re-added
    discardedCards = []
    hand = []

    def __init__(self, nDecks=1):
        for _ in range(nDecks):
            # every suite
            for s in ["H", "D", "C", "S"]:
                # every value
                for i in range(1, 14):
                    self.cards.append(Card(i, s))
        random.shuffle(self.cards)

    def draw(self):
        try:
            return self.cards.pop()
        except:
            self.reshuffle()
            return self.cards.pop()

    def reshuffle(self):
        random.shuffle(self.discardedCards)
        self.cards = self.discardedCards
        self.discardedCards = []

    def returnCards(self, cards):
        discardedCards += cards

    def __str__(self):
        repr = "\nDiamonds:"+str(selectSuite(self.cards, "Diamonds"))+"\nClubs:"+str(selectSuite(self.cards, "Clubs"))+"\nSpades:"+str(selectSuite(self.cards, "Spades"))+"\nHearts:"+str(selectSuite(self.cards, "Hearts"))
        return repr

class Dealer:

    def __init__(self, deck=None, startingHouseSize=2):
        if deck==None:
            self.deck = Deck()
        else:
            self.deck = deck
        self.pot = 0
        self.table = self.dealHand(startingHouseSize)

    def payOut(self, players):
        if len(players) == 1:
            players[0].addMoney(self.pot)
        else:
            # split pot if it's a tie
            for i in range(len(players)):
                players[i].addMoney(self.pot/len(players))
        self.pot = 0

    def dealHand(self, size=2):
        return [self.deck.draw() for _ in range(size)]

    def dealCard(self):
        return self.deck.draw()

    def returnCards(self, cards):
        self.deck.returnCards(cards)

    def endRound(self):
        self.table += self.deck.draw()

    def __str__(self):
        return "Deck: "+str(self.deck) + "\nCurrent Table: " + str(self.table) + "\nCurrent pot: " + str(self.pot)

class Player:
    def __init__(self, dealer, startingMoney=1000, openingHand=None):
        self.money = startingMoney
        self.dealer = dealer
        if openingHand == None:
            self.hand = dealer.dealHand()
        else:
            self.hand = openingHand
        self.latestBet = 0

    def addMoney(self, amount):
        self.money += amount

    def newHand(self):
        self.dealer.returnCards(self.hand)
        self.hand = self.dealer.dealHand()

    def bet(self, amount):
        # assumes that amount can be bet
        self.money -= amount
        self.dealer.pot += amount
        self.latestBet = amount

    def __str__(self):
        return "Player hand: " + str(self.hand) + "\nPlayer Money: " + str(self.money) + "\nMost Recent Bet: " + str(self.latestBet)


class GameStateData:
    def __init__( self, prevState = None, dealer = Dealer() ):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        if prevState != None:
            self.agentStates = self.copyAgentStates( prevState.agentStates )
        self.lose = False
        self.win = False
        self.isHandEnd = False
        self.isRoundEnd = False
        self.score = 0

    def deepCopy( self ):
        state = GameStateData( self )
        return state

    def copyAgentStates( self, agentStates ):
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append( agentState.copy() )
        return copiedStates

    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        if other == None: return False
        # TODO Check for type of other
        if not self.agentStates == other.agentStates: return False
        return True

    def initialize(self, numOpponentAgents):
        self.agentStates = []
        numPlayers = 0
        for i in range(numOpponentAgents):
            if numPlayers == numOpponentAgents: continue # Max ghosts reached already
            else: numPlayers += 1
            self.agentStates.append( AgentState(isPlayer, Player(dealer)))

class GameState:

    # static variable to keep track of visited States
    explore = set()

    def getAndResetExplored():
        tmp = GameState.explored.copy()
        GameState.explore = set()
        return tmp
    getAndResetExplored = staticmethod(getAndResetExplored)


    def initialize(self, numOpponents):
        self.data.initialize(numOpponents)

    def getLegalActions(self, agentIndex=0):
        """
        Returns the legal actions for the specified player
        """

        if self.isWin() or self.isLose(): return []

        if agentIndex == 0:
            return PlayerRules.getLegalActions(self)
        else:
            return OpponentRules.getLegalActions(self, agentIndex)

    def generateSuccessor(self, agentIndex, action):
        if self.isWin() or self.isLose(): raise Exception("Can\'t generate a successor for a terminal state")

        state = GameState(self)

        if agentIndex == 0:
            PlayerRules.applyAction(state, action)
        else:
            OpponentRules.applyAction(state, action, agentIndex)
        GameState.explored.add(self)
        GameState.explored.add(state)
        return state

    def getLegalPlayerActions(self):
        return self.getLegalActions(0)

    def generatePlayerSuccessor(self, action):
        return self.generateSuccessor(0, action)

    def isLose(self):
        return self.data.lose

    def isWin(self):
        return self.data.win

    def isRoundEnd(self):
        return self.data.roundEnd

    def isHandEnd(self):
        return self.data.handEnd

    def getPlayerState( self ):
        """
        Returns an AgentState object for player
        """
        return self.data.agentStates[0].copy()

    def getPlayerMoney( self ):
        return self.data.agentStates[0].getMoney()

    def getPlayerHand(self):
        return self.data.agentStates[0].getHand()

    def getOpponentStates( self ):
        return self.data.agentStates[1:]

    def getOpponentState( self, agentIndex ):
        if agentIndex == 0 or agentIndex >= self.getNumAgents():
            raise Exception("Invalid index passed to getOpponentState")
        return self.data.agentStates[agentIndex]

    def getOpponentMoney( self, agentIndex ):
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getOpponentMoney")
        return self.data.agentStates[agentIndex].getMoney()

    def getOpponentsMoney(self):
        return [s.getMoney() for s in self.getOpponentStates()]

    def getNumAgents( self ):
        return len( self.data.agentStates )

    def getScore( self ):
        return float(self.data.score)

    def __init__( self, prevState = None ):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState != None: # Initial state
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy( self ):
        state = GameState( self )
        state.data = self.data.deepCopy()
        return state

    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        return hasattr(other, 'data') and self.data == other.data

    def __hash__( self ):
        """
        Allows states to be keys of dictionaries.
        """
        return hash( self.data )

    def __str__( self ):

        return str(self.data)

try:
    import boinc
    _BOINC_ENABLED = True
except:
    _BOINC_ENABLED = False

class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    """
    # removed arg 2 "display"
    def __init__( self, agents, rules, startingIndex=0, muteAgents=False, catchExceptions=False ):
        self.agentCrashed = False
        self.agents = agents
        # self.display = display
        self.rules = rules
        self.startingIndex = startingIndex
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTimes = [0 for agent in agents]
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        import cStringIO
        self.agentOutput = [cStringIO.StringIO() for agent in agents]

    def getProgress(self):
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    def _agentCrash( self, agentIndex, quiet=False):
        "Helper method for handling agent crashes"
        if not quiet: traceback.print_exc()
        self.gameOver = True
        self.agentCrashed = True
        self.rules.agentCrash(self, agentIndex)

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agentIndex):
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        import cStringIO
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self):
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR


    def run( self ):
        """
        Main control loop for game play.
        """
        # self.display.initialize(self.state.data)
        self.numMoves = 0

        ###self.display.initialize(self.state.makeObservation(1).data)
        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if not agent:
                self.mute(i)
                # this is a null agent, meaning it failed to load
                # the other team wins
                print >>sys.stderr, "Agent %d failed to load" % i
                self.unmute()
                self._agentCrash(i, quiet=True)
                return
            if ("registerInitialState" in dir(agent)):
                self.mute(i)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.registerInitialState, int(self.rules.getMaxStartupTime(i)))
                        try:
                            start_time = time.time()
                            timed_func(self.state.deepCopy())
                            time_taken = time.time() - start_time
                            self.totalAgentTimes[i] += time_taken
                        except TimeoutFunctionException:
                            print >>sys.stderr, "Agent %d ran out of time on startup!" % i
                            self.unmute()
                            self.agentTimeout = True
                            self._agentCrash(i, quiet=True)
                            return
                    except Exception,data:
                        self._agentCrash(i, quiet=False)
                        self.unmute()
                        return
                else:
                    agent.registerInitialState(self.state.deepCopy())
                ## TODO: could this exceed the total time
                self.unmute()

        agentIndex = self.startingIndex
        numAgents = len( self.agents )

        while not self.gameOver:
            # Fetch the next agent
            agent = self.agents[agentIndex]
            move_time = 0
            skip_action = False
            # Generate an observation of the state
            if 'observationFunction' in dir( agent ):
                self.mute(agentIndex)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.observationFunction, int(self.rules.getMoveTimeout(agentIndex)))
                        try:
                            start_time = time.time()
                            observation = timed_func(self.state.deepCopy())
                        except TimeoutFunctionException:
                            skip_action = True
                        move_time += time.time() - start_time
                        self.unmute()
                    except Exception,data:
                        self._agentCrash(agentIndex, quiet=False)
                        self.unmute()
                        return
                else:
                    observation = agent.observationFunction(self.state.deepCopy())
                self.unmute()
            else:
                observation = self.state.deepCopy()

            # Solicit an action
            action = None
            self.mute(agentIndex)
            if self.catchExceptions:
                try:
                    timed_func = TimeoutFunction(agent.getAction, int(self.rules.getMoveTimeout(agentIndex)) - int(move_time))
                    try:
                        start_time = time.time()
                        if skip_action:
                            raise TimeoutFunctionException()
                        action = timed_func( observation )
                    except TimeoutFunctionException:
                        print >>sys.stderr, "Agent %d timed out on a single move!" % agentIndex
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return

                    move_time += time.time() - start_time

                    if move_time > self.rules.getMoveWarningTime(agentIndex):
                        self.totalAgentTimeWarnings[agentIndex] += 1
                        print >>sys.stderr, "Agent %d took too long to make a move! This is warning %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex])
                        if self.totalAgentTimeWarnings[agentIndex] > self.rules.getMaxTimeWarnings(agentIndex):
                            print >>sys.stderr, "Agent %d exceeded the maximum number of warnings: %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex])
                            self.agentTimeout = True
                            self._agentCrash(agentIndex, quiet=True)
                            self.unmute()
                            return

                    self.totalAgentTimes[agentIndex] += move_time
                    #print "Agent: %d, time: %f, total: %f" % (agentIndex, move_time, self.totalAgentTimes[agentIndex])
                    if self.totalAgentTimes[agentIndex] > self.rules.getMaxTotalTime(agentIndex):
                        print >>sys.stderr, "Agent %d ran out of time! (time: %1.2f)" % (agentIndex, self.totalAgentTimes[agentIndex])
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return
                    self.unmute()
                except Exception,data:
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                action = agent.getAction(observation)
            self.unmute()

            # Execute the action
            self.moveHistory.append( (agentIndex, action) )
            if self.catchExceptions:
                try:
                    self.state = self.state.generateSuccessor( agentIndex, action )
                except Exception,data:
                    self.mute(agentIndex)
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                self.state = self.state.generateSuccessor( agentIndex, action )

            # Change the display
            # self.display.update( self.state.data )
            ###idx = agentIndex - agentIndex % 2 + 1
            ###self.display.update( self.state.makeObservation(idx).data )

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)
            # Track progress
            if agentIndex == numAgents + 1: self.numMoves += 1
            # Next agent
            agentIndex = ( agentIndex + 1 ) % numAgents

            if _BOINC_ENABLED:
                boinc.set_fraction_done(self.getProgress())

        # inform a learning agent of the game result
        for agentIndex, agent in enumerate(self.agents):
            if "final" in dir( agent ) :
                try:
                    self.mute(agentIndex)
                    agent.final( self.state )
                    self.unmute()
                except Exception,data:
                    if not self.catchExceptions: raise
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
        # self.display.finish()
        print("finish")
