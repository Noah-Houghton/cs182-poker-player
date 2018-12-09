import util
import agents
import random

# define points per hand as constants
ROYALFLUSH = 32
STRAIGHTFLUSH = ROYALFLUSH - 1
FOUROFAKIND = STRAIGHTFLUSH - 1
FULLHOUSE = FOUROFAKIND - 1
FLUSH = FULLHOUSE - 1
STRAIGHT = FLUSH - 1
THREEOFAKIND = STRAIGHT - 1
TWOPAIR = THREEOFAKIND - 1
PAIR = TWOPAIR - 1


"""
Common set of functions for rules
"""
class Rules:

    def newGame( self, playerAgent, opponentAgents, dealer, quiet = False, catchExceptions=False):
        # agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        agents = [playerAgent] + opponentAgents
        initState = GameState()
        initState.initialize(len(agents) - 1, dealer)
        game = Game(agents, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        totalMoney = sum([astate.player.money for astate in initState.data.agentStates])
        print("setting total money to {}".format(totalMoney))
        game.state.winningMoney = totalMoney
        print("getWinningMoney = {}".format(game.state.getWinningMoney()))
        return game

    def isRoyalFlush(cards):
        royalFlush = [0, 10, 11, 12, 13]
        for c in cards:
            if c[0] in royalFlush:
                royalFlush.remove(c[0])
            else:
                return False
        return True
    isRoyalFlush = staticmethod(isRoyalFlush)

    def isFlush(cards):
        cards.sort()
        val = cards[0][0] - 1
        for c in cards:
            if c[0] == val+1:
                val+=1
            else:
                return False
        return True
    isFlush = staticmethod(isFlush)

    def highCard(hand):
        return max([card[0] for card in hand])
    highCard = staticmethod(highCard)

    def getWinningMoney(self):
        return self.winningMoney

    def process(self, state, game):
        """
        Checks to see whether it is time to end the current phase of the game.
        """
        if game.rules.handOver(state):
            print("\n\n The Round is Over! \n \n")
            victors = game.rules.determineVictors(game, state)
            dealer = state.getDealer()
            dealer.payOut(victors)
            state.data.oneRound = False
            for agentState in state.data.agentStates:
                if agentState.player.index == 0:
                    PlayerRules.newHand(state)
                    PlayerRules.checkBank(state)
                else:
                    OpponentRules.newHand(state, agentState.player.index)
                    OpponentRules.checkBank(state, agentState.player.index)
        if state.isWin(): self.win(state, game)
        if state.isLose(): self.lose(state, game)
        state.getDealer().hitTable()
        state.data.oneRound = True
    #     if state.isRoundEnd(): self.roundEnd(state, game)
    #     if state.isHandEnd(): self.handEnd(state, game)
    #
    # def roundEnd(self, state, game):
    #     game.roundComplete = True
    #
    # def handEnd(self, state, game):
    #     game.handComplete = True
    def win( self, state, game ):
        if not self.quiet: print "Player emerges victorious! Score: %d" % state.data.score
        game.gameOver = True

    def lose( self, state, game ):
        if not self.quiet: print "Player Lost! Score: %d" % state.data.score
        game.gameOver = True

    def determineVictors(game, gameState):
        agentStates = gameState.data.agentStates
        handsAndPlayers = []
        maxScore = float("-inf")
        bestPlayers = []
        atLeastOneRound = gameState.data.oneRound
        for astate in agentStates:
            if atLeastOneRound:
                if astate.player.isActive:
                    handsAndPlayers.append((astate.player.getHand(), astate.player))
            else:
                handsAndPlayers.append((astate.player.getHand(), astate.player))
        # print("determing victors out of {}".format(handsAndPlayers))
        for hand in handsAndPlayers:
            score = game.rules.evaluateHand(hand[0])
            # print("hand score = {}".format(score))
            maxScore = max(maxScore, score)
        for hand in handsAndPlayers:
            score = game.rules.evaluateHand(hand[0])
            if score == maxScore:
                bestPlayers.append(hand[1])
        return bestPlayers

    determineVictors = staticmethod( determineVictors )


"""
Defines a set of rules by which the player operates
"""
class PlayerRules(Rules):

    def getLegalActions(state):
        return Actions.getPossibleActions(state.getPlayerState())
    getLegalActions = staticmethod( getLegalActions )

    def newHand(state):
        print("new hand for player")
        dealer = state.getDealer()
        state.data.agentStates[0].player.newHand()
        dealer.newTable()
    newHand = staticmethod(newHand)


    def applyAction(state, action):
        player = state.getPlayerState().player
        if action is "Fold":
            player.fold()
        elif action is "Raise":
            # TODO: encode raise amt
            r = min(10, player.money)
            player.bet(player.dealer.getCallAmt() + r)
        elif action is "Call":
            player.bet(player.dealer.getCallAmt())
        elif action is "Double down":
            player.bet(player.dealer.getCallAmt() * 2)
        elif action is "All-in":
            player.bet(player.money)
    applyAction = staticmethod( applyAction )

    def evaluateHand(hand):
        diamonds = selectSuite(hand, "Diamonds")
        hearts = selectSuite(hand, "Hearts")
        clubs = selectSuite(hand, "Clubs")
        spades = selectSuite(hand, "Spades")
        suits = [diamonds, hearts, clubs, spades]
        nums = [selectValue(hand, i) for i in range(1, 14)]

        bestScore = 0
        hasPair = False
        hasTOK = False
        for num in nums:
            if len(num) == 4:
                bestScore = max(FOUROFAKIND, bestScore)
            if len(num) == 3:
                hasTOK = True
                if hasPair:
                    bestScore = max(FULLHOUSE, bestScore)
                else:
                    bestScore = max(THREEOFAKIND, bestScore)
            if len(num) == 2:
                if hasTOK:
                    bestScore = max(FULLHOUSE, bestScore)
                elif hasPair:
                    bestScore = max(TWOPAIR, bestScore)
                else:
                    bestScore = max(PAIR, bestScore)
                hasPair = True
        for suit in suits:
            if len(suit) == 5:
                if Rules.isRoyalFlush(suit):
                    bestScore = max(ROYALFLUSH, bestScore)
                elif Rules.isStraightFlush(suit):
                    bestScore = max(STRAIGHTFLUSH, bestScore)
                else:
                    bestScore = max(FLUSH, bestScore)
        return max(Rules.highCard(hand), bestScore)
    evaluateHand = staticmethod(evaluateHand)

    def handOver(state):
        if len(state.getDealer().getTable()) == 5:
            print("full 5 cards on the table")
            return True
        active = 0
        for astate in state.data.agentStates:
            if astate.player.isActive:
                active += 1
        if active <= 1:
            print("only one player remains")
            return True
        print("hand continues")
        return False
    handOver = staticmethod(handOver)

    def checkBank(gameState):
        print("we're takin it to the bank")
        currentMoney = gameState.getPlayerMoney()
        gameState.data.score = currentMoney
        print("Player money: {} of {}".format(currentMoney, gameState.getWinningMoney()))
        if currentMoney <= 0:
            gameState.data.lose = True
        if currentMoney == gameState.getWinningMoney():
            gameState.data.win = True
    checkBank = staticmethod( checkBank )

"""
Defines a set of rules by which the opponents operate
"""
class OpponentRules(Rules):
    def getLegalActions(agentIndex):
        return Actions.getPossibleActions(state.getPlayerState())
    getLegalActions = staticmethod( getLegalActions )

    def newHand(state, agentIndex):
        print("new opponent hand")
        dealer = state.getDealer()
        state.data.agentStates[agentIndex].player.newHand()
        dealer.newTable()
    newHand = staticmethod(newHand)

    def applyAction(state, action, agentIndex):
        player = state.getOpponentState(agentIndex).player
        if action is "Fold":
            player.fold()
        elif action is "Raise":
            # TODO: encode raise amt in action
            r = min(10, player.money)
            player.bet(player.dealer.getCallAmt() + r)
        elif action is "Call":
            player.bet(player.dealer.getCallAmt())
        elif action is "Double down":
            player.bet(player.getCallAmt() * 2)
        elif action is "All-in":
            player.bet(player.money)
    applyAction = staticmethod( applyAction )

    def evaluateHand(hand):
        diamonds = selectSuite(hand, "Diamonds")
        hearts = selectSuite(hand, "Hearts")
        clubs = selectSuite(hand, "Clubs")
        spades = selectSuite(hand, "Spades")
        suits = [diamonds, hearts, clubs, spades]
        nums = [selectValue(hand, i) for i in range(1, 14)]

        bestScore = 0
        hasPair = False
        hasTOK = False
        for num in nums:
            if len(num) == 4:
                bestScore = max(FOUROFAKIND, bestScore)
            if len(num) == 3:
                hasTOK = True
                if hasPair:
                    bestScore = max(FULLHOUSE, bestScore)
                else:
                    bestScore = max(THREEOFAKIND, bestScore)
            if len(num) == 2:
                if hasTOK:
                    bestScore = max(FULLHOUSE, bestScore)
                elif hasPair:
                    bestScore = max(TWOPAIR, bestScore)
                else:
                    bestScore = max(PAIR, bestScore)
                hasPair = True
        for suit in suits:
            if len(suit) == 5:
                if Rules.isRoyalFlush(suit):
                    bestScore = max(ROYALFLUSH, bestScore)
                elif Rules.isStraightFlush(suit):
                    bestScore = max(STRAIGHTFLUSH, bestScore)
                else:
                    bestScore = max(FLUSH, bestScore)
        return max(Rules.highCard(hand), bestScore)
    evaluateHand = staticmethod(evaluateHand)

    def checkBank(state, agentIndex):
        currentMoney = state.data.agentStates[agentIndex].getMoney()
        print("Opponent money: {} \\ {}".format(currentMoney, state.getWinningMoney()))
        if currentMoney <= 0:
            state.data.lose = True
        if currentMoney == state.getWinningMoney():
            state.data.win = True
    checkBank = staticmethod( checkBank )


class Actions:

    def getPossibleActions(agentState):
        money = agentState.player.getMoney()
        print("player money {}".format(money))
        currentBet = agentState.player.dealer.getCallAmt()
        currentBet = max(agentState.player.dealer.getAnte(), currentBet)
        print("current bet {}".format(currentBet))
        CL = "Call"
        FLD = "Fold"
        RS = "Raise"
        DD = "Double Down"
        AI = "All-In"
        actionList = [FLD]
        if 0 > money - currentBet:
            return actionList
        if money >= currentBet:
            actionList += [CL, AI]
        if money > currentBet:
            if money > 2 * currentBet:
                actionList += [RS, DD]
            else:
                actionList.append(RS)
        return actionList
    getPossibleActions = staticmethod(getPossibleActions)


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
        self.discardedCards += cards

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
        self.startingHouseSize = startingHouseSize
        self.table = self.dealHand(startingHouseSize)
        self.callAmt = 0
        self.ante = 5

    def getAnte(self):
        return self.ante

    def getTable(self):
        return self.table

    def payOut(self, players):
        if len(players) == 1:
            print("{} won the pot of {}".format(players[0], self.pot))
            players[0].addMoney(self.pot)
            # print("Money is now {}".format(players[0].getMoney()))
        else:
            # split pot if it's a tie
            for i in range(len(players)):
                # print("{} receiving {}".format(players[i], self.pot/len(players)))
                players[i].addMoney(self.pot/len(players))
        self.pot = 0
        self.callAmt = 0

    def newTable(self):
        self.returnCards(self.table)
        self.resetCall(5)
        self.table = self.dealHand(self.startingHouseSize)

    def dealNewHand(self, oldCards, size=2):
        self.returnCards(oldCards)
        return self.dealHand(size)

    def dealHand(self, size=2):
        return [self.deck.draw() for _ in range(size)]

    def updateCall(self, amount):
        callAmt = max(self.callAmt, amount)

    def resetCall(self, ante=5):
        self.ante = ante
        callAmt = self.ante

    def dealCard(self):
        return self.deck.draw()

    def hitTable(self):
        self.table.append(self.dealCard())

    def returnCards(self, cards):
        self.deck.returnCards(cards)

    def endRound(self):
        self.table += self.deck.draw()

    def getCallAmt(self):
        return self.callAmt

    def __str__(self):
        return "Deck: "+str(self.deck) + "\nCurrent Table: " + str(self.table) + "\nCurrent pot: " + str(self.pot)

class Player:
    def __init__(self, dealer, index, startingMoney=1000, openingHand=None):
        self.money = startingMoney
        self.dealer = dealer
        self.index = index
        if openingHand == None:
            self.hand = dealer.dealHand()
        else:
            self.hand = openingHand
        self.latestBet = 0
        self.isActive = True

    def addMoney(self, amount):
        self.money += amount

    def newHand(self):
        self.isActive = True
        newHand = self.dealer.dealNewHand(self.hand)
        self.hand = newHand

    def bet(self, amount):
        # assumes that amount can be bet
        self.isActive = True
        self.money -= amount
        self.dealer.pot += amount
        self.latestBet = amount
        self.dealer.updateCall(amount)

    def fold(self):
        self.latestBet = 0
        self.isActive = False

    def getLatestBet(self):
        return self.latestBet

    def getMoney(self):
        return self.money

    def getHand(self):
        return self.hand

    def getDealer(self):
        return self.dealer

    def __str__(self):
        if self.isActive:
            header = "Active"
        else:
            header = "Inactive"
        return header + " Player {} hand: ".format(self.index) + str(self.hand) + "\nPlayer Money: " + str(self.money) + "\nMost Recent Bet: " + str(self.latestBet)

    def __hash__(self):
        return hash(hash(self.money) * hash(self.hand[0]))

class GameStateData:
    def __init__( self, prevState = None, dealer = Dealer() ):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        if prevState != None:
            self.agentStates = self.copyAgentStates( prevState.agentStates )
        self.lose = False
        self.win = False
        self.score = 0
        self.oneRound = False
        self.winningMoney = 0

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

    def __hash__(self):
        return hash(hash(self.score) * hash(self.agentStates[0]))

    def initialize(self, numOpponentAgents, dealer):
        self.agentStates = []
        numPlayers = 0
        for i in range(numOpponentAgents+1):
            print("init agent {}".format(i))
            if numPlayers == numOpponentAgents+1: continue # Max ghosts reached already
            else: numPlayers += 1
            player = Player(dealer, i)
            print("Player money: {}".format(player.getMoney()))
            self.winningMoney += player.money
            self.agentStates.append( AgentState(i==0, player))

class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    """

    def __init__( self, isPlayer, player ):
        self.isPlayer = isPlayer
        self.player = player

    def __str__( self ):
        if self.isPlayer:
            return "player: " + str( self.player )
        else:
            return "opponent: " + str( self.player )

    def __eq__( self, other ):
        if other == None:
            return False
        return self.player == other.player

    def __hash__(self):
        return hash(self.player)

    def copy( self ):
        state = AgentState( self.isPlayer, self.player )
        return state

    def getMoney(self):
        return self.player.getMoney()

    def getBet(self):
        return self.player.getBet()

    def getHand(self):
        return self.player.getHand()

    def getDealer(self):
        return self.player.getDealer()


class GameState:

    # static variable to keep track of visited States
    explored = set()

    def getAndResetExplored():
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp
    getAndResetExplored = staticmethod(getAndResetExplored)


    def initialize(self, numOpponents, dealer):
        self.data.initialize(numOpponents, dealer)

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

    def isAtLeastOneRound(self):
        return self.data.oneRound

    def getPlayerState( self ):
        """
        Returns an AgentState object for player
        """
        return self.data.agentStates[0].copy()

    def getWinningMoney(self):
        return self.data.winningMoney

    def getPlayerMoney( self ):
        return self.data.agentStates[0].getMoney()

    def getPlayerBet(self):
        return self.data.agentStates[0].getBet()

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

    def getDealer(self):
        return self.data.agentStates[0].getDealer()

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
        print("we're running!")

        while not self.gameOver:
            print("loop beginning for agent {}".format(agentIndex))
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
            print(action)

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
