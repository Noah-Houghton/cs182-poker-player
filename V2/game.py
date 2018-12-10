import util
# import agents
import random


"""

INSTRUCTIONS TO RUN FROM THE COMMAND LINE
*****************************************
import game
import agents
player = agents.ReflexAgent()
opponents = []
# do this as many times as you want opponent agents
opponents.append(agents.ReflexAgent())
rules = game.Rules()
ng = rules.newGame(player, opponents)
ng.run()

"""



# define points per hand as constants
ROYALFLUSH = 32
STRAIGHTFLUSH = ROYALFLUSH - 1 #31
FOUROFAKIND = STRAIGHTFLUSH - 1 #30
FULLHOUSE = FOUROFAKIND - 1 #29
FLUSH = FULLHOUSE - 1 #28
STRAIGHT = FLUSH - 1 #27
THREEOFAKIND = STRAIGHT - 1 #26
TWOPAIR = THREEOFAKIND - 1 #25
PAIR = TWOPAIR - 1 #24


"""
Common set of functions for rules
"""
class Rules:

    def newGame( self, playerAgent, opponentAgents, quiet = False, catchExceptions=False):
        # agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        i = 1
        for agent in opponentAgents:
            agent.index = i
            i += 1
        agents = [playerAgent] + opponentAgents
        initState = GameState()
        initState.initialize(len(agents) - 1)
        game = Game(agents, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        print("getWinningMoney = {}".format(game.state.getWinningMoney()))
        return game

    def newHand(state, agentIndex=0):
        print("new hand for {}".format(agentIndex))
        state.data.agentStates[agentIndex].newHand(state)
        state.data.newTable()
    newHand = staticmethod(newHand)

    def isRoyalFlush(cards):
        royalFlush = [0, 10, 11, 12, 13]
        for c in cards:
            if c[0] in royalFlush:
                royalFlush.remove(c[0])
            else:
                return False
        return True
    isRoyalFlush = staticmethod(isRoyalFlush)

    def isStraightFlush(cards):
        cards.sort()
        val = cards[0][0] - 1
        for c in cards:
            if c[0] == val+1:
                val+=1
            else:
                return False
        return True
    isStraightFlush = staticmethod(isStraightFlush)

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

    def evaluateHand(hand):
        diamonds = selectSuite(hand, "Diamonds")
        hearts = selectSuite(hand, "Hearts")
        clubs = selectSuite(hand, "Clubs")
        spades = selectSuite(hand, "Spades")
        suits = [diamonds, hearts, clubs, spades]
        nums = [selectValue(hand, i) for i in range(1, 14)]
        nums.sort(key=len)
        suits.sort(key=len)

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
        if len(state.getTable()) == 5 and state.isRoundComplete:
            print("full 5 cards on the table")
            return True
        active = 0
        for astate in state.data.agentStates:
            if not astate.hasFolded:
                active += 1
        if active == 1:
            print("only one player remains")
            return True
        return False
    handOver = staticmethod(handOver)

    def process(self, state, game):
        """
        Checks to see whether it is time to end the current phase of the game.
        """
        if Rules.handOver(state):
            print("\n\n The Round is Over! \n \n")
            state.payOut()
            state.roundComplete(False)
            for agentState in state.data.agentStates:
                print(agentState)
                if agentState.index == 0:
                    PlayerRules.newHand(state)
                    PlayerRules.checkBank(state)
                else:
                    OpponentRules.newHand(state, agentState.index)
                    OpponentRules.checkBank(state, agentState.index)

            # nr = input("press any key to continue to next round: ")
        if state.isWin(): self.win(state, game)
        if state.isLose(): self.lose(state, game)
        if state.isRoundComplete():
            # nextCard = input("next card")
            state.roundComplete(False)
            state.hitTable()
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

    def determineVictors(gameState):
        agentStates = gameState.data.agentStates
        handsAndPlayers = []
        maxScore = float("-inf")
        bestPlayers = []
        for astate in agentStates:
            if not astate.hasFolded:
                handsAndPlayers.append((astate.getHand(), astate))
        # print("determining victors out of {}".format(handsAndPlayers))
        if len(handsAndPlayers) == 1:
            return [handsAndPlayers[0][1]]
        for hand in handsAndPlayers:
            cards = list(hand[0])
            # add the table to the player's hand
            cards += gameState.getTable()
            # print("checking cards {}".format(cards))
            score = Rules.evaluateHand(cards)
            # print("calculating score {}".format(score))
            maxScore = max(maxScore, score)
        for hand in handsAndPlayers:
            cards = list(hand[0])
            cards += gameState.getTable()
            # print("checking cards again {}".format(c))
            score = Rules.evaluateHand(cards)
            # print("checking score again {}".format(s))
            if score == maxScore:
                bestPlayers.append(hand[1])
        return bestPlayers

    determineVictors = staticmethod( determineVictors )


"""
Defines a set of rules by which the player operates
"""
class PlayerRules(Rules):

    def getLegalActions(state):
        print("getting player actions")
        return Actions.getPossibleActions(state, 0)
    getLegalActions = staticmethod( getLegalActions )

    def applyAction(state, action):
        betAmt = 0
        if action == "Fold":
            betAmt = 0
        elif action == "Raise":
            # TODO: encode raise amt
            r = min(10, state.getPlayerMoney() - state.getCallAmt())
            betAmt = state.getCallAmt() + r
        elif action == "Call":
            betAmt = state.getCallAmt()
        elif action == "Double Down":
            betAmt = state.getCallAmt() * 2
        elif action == "All-In":
            betAmt = state.getPlayerMoney()
        else:
            raise Exception("Player Action not recognized")
        state.bet(betAmt)
    applyAction = staticmethod( applyAction )


    def checkBank(gameState):
        currentMoney = gameState.getPlayerMoney()
        gameState.data.score = currentMoney
        print("Player money: {} of {}".format(currentMoney, gameState.getWinningMoney()))
        if currentMoney < 0:
            raise Exception("Player cannot have negative money")
        if (currentMoney == 0 or currentMoney - gameState.data.getAnte() <= 0) and Rules.handOver(gameState):
            print("player has lost")
            gameState.data.lose = True
        if currentMoney == gameState.getWinningMoney():
            print("player has won")
            gameState.data.win = True
    checkBank = staticmethod( checkBank )

"""
Defines a set of rules by which the opponents operate
"""
class OpponentRules(Rules):
    def getLegalActions(state, agentIndex):
        print("getting opponent actions")
        return Actions.getPossibleActions(state, agentIndex)
    getLegalActions = staticmethod( getLegalActions )

    def applyAction(state, action, agentIndex):
        betAmt = 0
        if action == "Fold":
            betAmt = 0
        elif action == "Raise":
            # TODO: encode raise amt in action
            r = min(10, state.getOpponentMoney(agentIndex) - state.getCallAmt())
            betAmt = r + state.getCallAmt()
        elif action == "Call":
            betAmt = state.getCallAmt()
        elif action == "Double Down":
            betAmt = state.getCallAmt() * 2
        elif action == "All-In":
            betAmt = state.getOpponentMoney(agentIndex)
        else:
            raise Exception("Opponent Action not recognized")
        state.bet(betAmt, agentIndex)
        # print("Opponent {} has bet {}".format(agentIndex, betAmt))
        # print("Money is now {}".format(state.getOpponentMoney(agentIndex)))
    applyAction = staticmethod( applyAction )


    def checkBank(state, agentIndex):
        currentMoney = state.getOpponentMoney(agentIndex)
        print("Opponent money: {} \\ {}".format(currentMoney, state.getWinningMoney()))
        if currentMoney < 0:
            raise Exception("Agent cannot have negative money")
        # if currentMoney <= 0:
            # state.data.win = True
        if currentMoney == state.getWinningMoney():
            state.data.lose= True
    checkBank = staticmethod( checkBank )


class PokerMoves:

    CALL = "Call"
    FOLD = "Fold"
    RAISE = "Raise"
    DOUBLEDOWN = "Double Down"
    ALLIN = "All-In"

class Actions:
    def getPossibleActions(state, agentIndex):
        call = state.getCallAmt()
        bet = state.data.agentStates[agentIndex].getBet()
        agentMoney = state.data.agentStates[agentIndex].getMoney()
        actionList = [PokerMoves.FOLD]
        actAmt = max(call, bet)
        moneyAfterAction = agentMoney - actAmt
        if moneyAfterAction < 0:
            return actionList
        if moneyAfterAction >= 0:
            actionList += [PokerMoves.CALL, PokerMoves.ALLIN]
        # right now we just raise 10
        if moneyAfterAction > 0:
            if agentMoney > 2 * actAmt:
                actionList += [PokerMoves.RAISE, PokerMoves.DOUBLEDOWN]
            else:
                actionList.append(PokerMoves.RAISE)
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

class GameStateData:
    def __init__( self, prevState = None, deck = Deck() ):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        if prevState != None:
            self.agentStates = self.copyAgentStates( prevState.agentStates )
            self.lose = prevState.lose
            self.win = prevState.win
            self.score = prevState.score
            self.winningMoney = prevState.winningMoney
            self.roundComplete = prevState.roundComplete
            self.pot = prevState.pot
            self.ante = prevState.ante
            self.call = prevState.call
            self.table = prevState.table
            self.startingHouseSize = prevState.startingHouseSize
            self.deck = prevState.deck
            self.calledPlayers = prevState.calledPlayers
        else:
            self.lose = False
            self.win = False
            self.score = 0
            self.roundComplete = False
            self.pot = 0
            self.ante = 5
            self.call = self.ante
            self.startingHouseSize = 2
            self.deck = deck
            self.table = self.dealHand(self.startingHouseSize)
            self.startingMoney = 1000
            self.calledPlayers = []

    def getTable(self):
        return self.table

    def newTable(self):
        self.returnCards(self.table)
        self.resetCall()
        self.table = self.dealHand(self.startingHouseSize)

    def dealNewHand(self, oldCards, size=2):
        self.returnCards(oldCards)
        return self.dealHand(size)

    def dealHand(self, size=2):
        return [self.deck.draw() for _ in range(size)]

    def dealCard(self):
        return self.deck.draw()

    def hitTable(self):
        draw = self.dealCard()
        print("dealer drew {}".format(draw))
        self.table.append(draw)
        print("Pot is {}".format(self.getPot()))
        print("table is now {}".format(self.table))

    def returnCards(self, cards):
        self.deck.returnCards(cards)

    def getWinningMoney(self):
        return self.winningMoney

    def updateCall(self, amount):
        self.call = max(self.call, amount)

    def resetCall(self):
        self.call = self.ante

    def getCallAmt(self):
        return self.call

    def getAnte(self):
        return self.ante

    def resetPot(self):
        self.pot = 0

    def addPot(self, amount):
        self.pot += amount

    def getPot(self):
        return self.pot

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

    def initialize(self, numOpponentAgents):
        self.agentStates = []
        self.winningMoney = 0
        numPlayers = 0
        for i in range(numOpponentAgents+1):
            print("init agent {}".format(i))
            if numPlayers == numOpponentAgents+1: continue # Max ghosts reached already
            else: numPlayers += 1
            astate = AgentState(i == 0)
            astate.initialize(i, self)
            self.winningMoney += astate.getMoney()
            self.agentStates.append(astate)
            self.calledPlayers.append(False)



class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    """

    def __init__( self, isPlayer ):
        self.isPlayer = isPlayer
        self.hasFolded = False

    def initialize(self, index, gameStateData):
        self.latestBet = 0
        self.index = index
        self.money = gameStateData.startingMoney
        self.hand = gameStateData.dealHand()

    def addMoney(self, amount):
        self.money += amount

    def newHand(self, gameState):
        self.hand = gameState.newHand(self.hand)
        self.hasFolded = False

    def __str__( self ):
        if self.isPlayer:
            return "player: " + str( self.index )
        else:
            return "opponent: " + str( self.index )

    def __eq__( self, other ):
        if other == None:
            return False
        return self.money == other.money and self.hand == other.hand

    def __hash__(self):
        return hash(self.money)

    def __str__(self):
        return "Agent {} | Hand: {}".format(self.index, self.hand)

    def __repr__(self):
        return "Agent {} | Hand Value: {}".format(self.index, Rules.evaluateHand(self.hand))


    def copy( self ):
        state = AgentState( self.isPlayer )
        state.hasFolded = self.hasFolded
        state.latestBet = self.latestBet
        state.index = self.index
        state.money = self.money
        state.hand = self.hand
        return state

    def getMoney(self):
        return self.money

    def getBet(self):
        return self.latestBet

    def bet(self, gameState, amount):
        # assumes that amount can be bet
        if amount == 0:
            self.hasFolded = True
        else:
            self.hasFolded = False
            if amount == gameState.data.getCallAmt():
                gameState.hasCalled(self.index)
            # if we're not meeting the call, we must be changing it
            else:
                gameState.updateCall(amount)
                gameState.resetCalledPlayers(self.index)
            self.money -= amount
            gameState.addPot(amount)
        self.latestBet = amount

    def getHand(self):
        return self.hand

class GameState:

    # static variable to keep track of visited States
    explored = set()

    def getAndResetExplored():
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp
    getAndResetExplored = staticmethod(getAndResetExplored)

    def updateCall(self, amount):
        self.data.updateCall(amount)

    def newHand(self, hand):
        return self.data.dealNewHand(hand)

    def addPot(self, amount):
        self.data.addPot(amount)

    def hasCalled(self, playerIndex):
        self.data.calledPlayers[playerIndex] = True

    def resetCalledPlayers(self, playerIndex):
        for i in self.data.calledPlayers:
            i = False
        self.data.calledPlayers[playerIndex] = True

    def playerHasCalled(self, playerIndex):
        return self.data.calledPlayers[playerIndex]

    def payOut(self):
        agentStates = Rules.determineVictors(self)
        if len(agentStates) == 1:
            agentStates[0].addMoney(self.data.getPot())
            print("{} won the pot! Adding {}".format(agentStates[0], self.data.getPot()))
        else:
            # split pot if it's a tie
            print("splitting pot {} {} ways across players {}.".format(self.data.getPot(), len(agentStates), agentStates))
            for i in range(len(agentStates)):
                if self.data.getPot() % len(agentStates) != 0:
                    agentStates[i].addMoney(self.data.getPot()/len(agentStates))
                    print("{} receives {}".format(agentStates[i], self.data.getPot()/len(agentStates)))
                    # naively just give the total remainder to the first person
                    if i == 0:
                        agentStates[i].addMoney(self.data.getPot() % len(agentStates))
                        print("{} got the remainder {}".format(agentStates[i], self.data.getPot() % len(agentStates)))
                else:
                    agentStates[i].addMoney(self.data.getPot()/len(agentStates))
                    print("{} receives {}".format(agentStates[i], self.data.getPot()/len(agentStates)))

        self.data.resetPot()
        self.callAmt = self.data.getAnte()

    def isRoundComplete(self):
        return self.data.roundComplete

    def roundComplete(self, b):
        self.data.roundComplete = b

    def initialize(self, numOpponents):
        self.data.initialize(numOpponents)

    def getLegalActions(self, agentIndex=0):
        """
        Returns the legal actions for the specified player
        """

        if self.isWin() or self.isLose(): return []

        if agentIndex == 0:
            print("getting player legal actions")
            return PlayerRules.getLegalActions(self)
        else:
            print("getting opponent legal actions")
            return OpponentRules.getLegalActions(self, agentIndex)

    def generateSuccessor(self, agentIndex, action):
        if self.isWin() or self.isLose(): raise Exception("Can\'t generate a successor for a terminal state")

        state = GameState(self)

        if agentIndex == 0:
            print("generating player successor")
            PlayerRules.applyAction(state, action)
        else:
            print("generating opponent successor")
            OpponentRules.applyAction(state, action, agentIndex)
        state.data._agentMoved = agentIndex
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

    def bet(self, amount, playerIndex=0):
        self.data.agentStates[playerIndex].bet(self, amount)

    def getPlayerState( self ):
        """
        Returns an AgentState object for player
        """
        return self.data.agentStates[0]
        # removed .copy()

    def getWinningMoney(self):
        return self.data.getWinningMoney()

    def getPlayerMoney( self ):
        return self.data.agentStates[0].getMoney()

    def getPlayerBet(self):
        return self.data.agentStates[0].getBet()

    def getPlayerHand(self):
        return self.data.agentStates[0].getHand()

    def getOpponentStates( self ):
        return self.data.agentStates[1:]

    def getOpponentBet(self, agentIndex):
        return self.data.agentStates[agentIndex].getBet()

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

    def getTable(self):
        return self.data.getTable()

    def hitTable(self):
        self.data.hitTable()

    def getCallAmt(self):
        return self.data.getCallAmt()

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
            # print("loop beginning for agent {}".format(agentIndex))
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
            print("{} selected action: {}. Remaining Money: {}. Bet: {}".format(agentIndex, action, self.state.data.agentStates[agentIndex].getMoney(), self.state.data.agentStates[agentIndex].getBet()))
            # Change the display
            # self.display.update( self.state.data )
            ###idx = agentIndex - agentIndex % 2 + 1
            ###self.display.update( self.state.makeObservation(idx).data )

            # Track progress
            if agentIndex == numAgents - 1:
                self.numMoves += 1
                self.state.roundComplete(True)
                # all players have either called or folded
                for a in self.state.data.agentStates:
                    if not (a.hasFolded or self.state.playerHasCalled(a.index)):
                        print("called {}, folded {}, round continues".format(a.hasFolded, self.state.playerHasCalled(a.index)))
                        self.state.roundComplete(False)
            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)
            # Next agent
            agentIndex = ( agentIndex + 1 ) % numAgents
            # print("next agent: {}".format(agentIndex))
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
