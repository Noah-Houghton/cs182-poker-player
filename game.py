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
rules = game.ClassicGameRules()
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
class ClassicGameRules:

    def __init__(self, timeout=30):
        self.timeout = timeout

    def newGame( self, playerAgent, opponentAgents, quiet = False, catchExceptions=False, suppressPrint=False):
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
        self.suppressPrint = suppressPrint
        # print("getWinningMoney = {}".format(game.state.getWinningMoney()))
        return game

    def newHand(state, agentIndex=0):
        # print("new hand for {}".format(agentIndex))
        state.data.agentStates[agentIndex].newHand(state)
        # state.data.newTable()
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
                if ClassicGameRules.isRoyalFlush(suit):
                    bestScore = max(ROYALFLUSH, bestScore)
                elif ClassicGameRules.isStraightFlush(suit):
                    bestScore = max(STRAIGHTFLUSH, bestScore)
                else:
                    bestScore = max(FLUSH, bestScore)
        return max(ClassicGameRules.highCard(hand), bestScore)
    evaluateHand = staticmethod(evaluateHand)

    def handOver(state):
        if len(state.getTable()) == 5 and state.isRoundComplete:
            # print("full 5 cards on the table")
            return True
        active = state.data.getNumActivePlayers()
        if (active == 1):
            # print("only one player active")
            return True
        # print("{} active".format(active))
        return False
    handOver = staticmethod(handOver)

    def process(self, state, game):
        """
        Checks to see whether it is time to end the current phase of the game.
        """
        if ClassicGameRules.handOver(state):
            potValue = state.data.getPot()
            state.payOut()
            if not game.rules.suppressPrint:
                state.printBoard(potValue)
            state.roundComplete(False)
            state.mustAnte()
            totalMoney = 0
            for agentState in state.data.agentStates:
                # print(agentState)
                if agentState.index == 0:
                    PlayerRules.newHand(state)
                    PlayerRules.checkBank(state)
                    totalMoney += state.getPlayerMoney()
                else:
                    OpponentRules.newHand(state, agentState.index)
                    OpponentRules.checkBank(state, agentState.index)
                    totalMoney += state.getOpponentMoney(agentState.index)
            if totalMoney != state.getWinningMoney():
                raise Exception("money has been lost: only found {}".format(totalMoney))
            if not (state.isWin() or state.isLose()):
                state.data.newTable()
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
        if not self.quiet and not self.suppressPrint: print "Player emerges victorious! Score: %d" % state.data.score
        game.gameOver = True

    def lose( self, state, game ):
        if not self.quiet and not self.suppressPrint: print "Player Lost! Score: %d" % state.data.score
        game.gameOver = True

    def determineVictors(gameState):
        agentStates = gameState.data.agentStates
        handsAndPlayers = []
        maxScore = float("-inf")
        bestPlayers = []
        for astate in agentStates:
            if not astate.getHasFolded():
                handsAndPlayers.append((astate.getHand(), astate))
        # print("determining victors out of {}".format(handsAndPlayers))
        if len(handsAndPlayers) == 1:
            return [handsAndPlayers[0][1]]
        for hand in handsAndPlayers:
            cards = list(hand[0])
            # add the table to the player's hand
            cards += gameState.getTable()
            # print("checking cards {}".format(cards))
            score = ClassicGameRules.evaluateHand(cards)
            # print("calculating score {}".format(score))
            maxScore = max(maxScore, score)
        for hand in handsAndPlayers:
            cards = list(hand[0])
            cards += gameState.getTable()
            # print("checking cards again {}".format(c))
            score = ClassicGameRules.evaluateHand(cards)
            # print("checking score again {}".format(s))
            if score == maxScore:
                bestPlayers.append(hand[1])
        return bestPlayers

    determineVictors = staticmethod( determineVictors )


"""
Defines a set of rules by which the player operates
"""
class PlayerRules(ClassicGameRules):

    def getLegalActions(state):
        # print("getting player actions")
        return Actions.getPossibleActions(state, 0)
    getLegalActions = staticmethod( getLegalActions )

    def applyAction(state, action):
        betAmt = PokerMoves.moveToCost(action, state)
        # print("applying {}, cost {}".format(action, betAmt))
        state.bet(betAmt)
    applyAction = staticmethod( applyAction )


    def checkBank(gameState):
        currentMoney = gameState.data.agentStates[0].getMoney()
        gameState.data.score = currentMoney
        if currentMoney < 0:
            raise Exception("Player cannot have negative money")
        if (currentMoney - gameState.data.getAnte() < 0) and gameState.getPlayerBet() == 0:
            gameState.data.lose = True
        # check to see if opponents can't make ante
        opponentsCanContinue = False
        for a in gameState.data.agentStates:
            if a.index != 0:
                if a.getMoney() >= gameState.data.getAnte():
                    opponentsCanContinue = True
        if currentMoney == gameState.getWinningMoney() or not opponentsCanContinue:
            # print("player has won")
            gameState.data.win = True
    checkBank = staticmethod( checkBank )

"""
Defines a set of rules by which the opponents operate
"""
class OpponentRules(ClassicGameRules):
    def getLegalActions(state, agentIndex):
        # print("getting opponent actions")
        return Actions.getPossibleActions(state, agentIndex)
    getLegalActions = staticmethod( getLegalActions )

    def applyAction(state, action, agentIndex):
        betAmt = PokerMoves.moveToCost(action, state, agentIndex)
        state.bet(betAmt, agentIndex)
    applyAction = staticmethod( applyAction )


    def checkBank(state, agentIndex):
        currentMoney = state.getOpponentMoney(agentIndex)
        # print("Opponent money: {} \\ {}".format(currentMoney, state.getWinningMoney()))
        if currentMoney < 0:
            raise Exception("Agent cannot have negative money")
        if currentMoney == state.getWinningMoney():
            state.data.lose= True
    checkBank = staticmethod( checkBank )


class PokerMoves:
"""
To add a move to the game:
1. Define it as below
2. Add it to the movesAsList list
3. Add relevant logic to moveToCost function
"""


    CALL = "Call"
    FOLD = "Fold"
    RAISE = "Raise"
    LARGERAISE  = "Large Raise"
    DOUBLEDOWN = "Double Down"
    ALLIN = "All-In"

    movesAsList = [CALL,FOLD,RAISE,LARGERAISE,DOUBLEDOWN,ALLIN]

    def moveToCost(move, gameState, agentIndex=0):
        # print("calculating cost of {}".format(move))
        # smallBlind = agentState.getSmallBlind()
        smallBlind = 10
        # largeBlind = agentState.getLargeBlind()
        largeBlind = 20
        call = gameState.data.getCallAmt()
        agentMoney = 0
        if agentIndex == 0:
            agentMoney = gameState.getPlayerMoney()
        else:
            agentMoney = gameState.getOpponentMoney(agentIndex)
        cost = 0
        if move == PokerMoves.CALL:
            cost = call
        elif move == PokerMoves.ALLIN:
            cost = agentMoney
        elif move == PokerMoves.RAISE:
            cost = call + smallBlind
        elif move == PokerMoves.LARGERAISE:
            cost = call + largeBlind
        elif move == PokerMoves.DOUBLEDOWN:
            cost = call * 2
        elif move == PokerMoves.FOLD:
            cost = 0
        else:
            raise Exception("Action not Recognized")
        return cost
    moveToCost = staticmethod(moveToCost)

class Actions:

    def getPossibleActions(state, agentIndex):
        # enforce invariant that a folded agent cannot bet anymore
        if state.data.agentStates[agentIndex].getHasFolded():
            return [PokerMoves.FOLD]
        call = state.getCallAmt()
        # print("most recent bet {}".format(state.data.agentStates[agentIndex].getBet()))
        agentMoney = state.data.agentStates[agentIndex].getMoney()
        # if player cannot make call, either all-in as ante or fold
        if agentMoney - call < 0:
            if state.data.getIsAnte():
                return [PokerMoves.ALLIN]
            else:
                return [PokerMoves.FOLD]
        possibleActions = []
        for move in PokerMoves.movesAsList:
            cost = PokerMoves.moveToCost(move, state, agentIndex)
            # print("action {} for agent {} results in agent money {}".format(move, agentIndex, agentMoney-cost))
            if agentMoney - cost >= 0:
                possibleActions.append(move)
                if state.data.agentStates[agentIndex].getMoney() - cost < 0:
                    raise Exception("move results in negative money")
        # prune/override moves as necessary
        # if agent can ante, it must do so
        if state.data.getIsAnte() and agentMoney >= state.data.getAnte():
            possibleActions.remove(PokerMoves.FOLD)
        if possibleActions == []:
            raise Exception("Cannot return no possible actions")
        return possibleActions
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

def cardToString(card):
    rank = card[0]
    suite = card[1]
    str = "{} of {}".format(rank, suite)
    return str

def handToString(hand):
    handstr = ""
    for card in hand:
        handstr += cardToString(card) + ", "
    return handstr[:-2]



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

class GameStateData:
    def __init__( self, prevState = None, nDecks=1 ):
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
            self.calledPlayers = prevState.calledPlayers
            self.nDecks = prevState.nDecks
            self.defaultDeck = prevState.defaultDeck
            self.cards = prevState.cards
            self.discardedCards = prevState.discardedCards
            self.drawnCards = prevState.drawnCards
            self.deckSize = prevState.deckSize
            self.startingDeck = prevState.startingDeck
            self.mustAnte = prevState.mustAnte
        else:
            self.lose = False
            self.win = False
            self.score = 0
            self.roundComplete = False
            self.mustAnte = True
            self.pot = 0
            self.ante = 5
            self.call = self.ante
            self.startingHouseSize = 2
            self.startingMoney = 1000
            self.calledPlayers = []
            self.nDecks = nDecks
            self.defaultDeck = None
            self.discardedCards = []
            self.drawnCards = []
            self.deckSize = nDecks * 4 * 13
            # initialize deck
            self.cards = []
            for _ in range(nDecks):
                # every suite
                for s in ["H", "D", "C", "S"]:
                    # every value
                    for i in range(1, 14):
                        self.cards.append(Card(i, s))
            random.shuffle(self.cards)
            self.startingDeck = list(self.cards)
            # initialize table
            self.table = self.dealHand(self.startingHouseSize)

    def getIsAnte(self):
        return self.mustAnte

    def getNumActivePlayers(self):
        num = 0
        for astate in self.agentStates:
            if not astate.getHasFolded() or not astate.getBet() == 0:
                if (astate.getMoney() > self.getCallAmt()) or (self.playerHasCalled(astate.index)):
                    num += 1
        return num

    def playerHasCalled(self, agentIndex):
        return self.calledPlayers[agentIndex]


    def draw(self):
        try:
            card = self.cards.pop()
        except:
            self.reshuffle()
            card = self.cards.pop()
        self.drawnCards.append(card)
        if card in self.discardedCards:
            raise Exception("dealt a discarded card")
        return card

    def reshuffle(self):
        self.cards = list(self.discardedCards)
        self.cards.sort()
        self.discardedCards = []
        if len(self.discardedCards) + len(self.drawnCards) + len(self.cards) != self.deckSize:
            raise Exception("cards missing")

    def returnCards(self, cards):
        for card in cards:
            # print("returning card {}".format(card))
            self.discardedCards.append(card)
            self.drawnCards.remove(card)
        # print("discarded now {}".format(self.discardedCards))
        if len(self.discardedCards) == self.deckSize:
            self.reshuffle()


    def getTable(self):
        return self.table

    def newTable(self):
        self.resetCall()
        # print("returning table {}".format(self.table))
        self.table = self.dealNewHand(self.table, self.startingHouseSize)
        # print("new table {}".format(self.table))

    def dealNewHand(self, oldCards, size=2):
        # print("dealing a new hand, returning {}".format(oldCards))
        if oldCards == [] or oldCards == None:
            raise Exception("attempting to return 0 cards")
        self.returnCards(oldCards)
        return self.dealHand(size)

    def dealHand(self, size=2):
        cards = []
        for _ in range(size):
            cards.append(self.draw())
        return cards

    def dealCard(self):
        return self.draw()

    def hitTable(self):
        draw = self.dealCard()
        # print("dealer drew {}".format(draw))
        self.table.append(draw)
        # print("Pot is {}".format(self.getPot()))
        # print("table is now {}".format(self.table))

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
            # print("init agent {}".format(i))
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

    def getHasFolded(self):
        return self.hasFolded

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
        return "Agent {} | Hand Value: {}".format(self.index, ClassicGameRules.evaluateHand(self.hand))


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
        # print("betting amount {}".format(amount))
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
            if self.money < 0:
                raise Exception("No agent can have negative money ({})".format(self.money))
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


    def printBoard(self, potValue):
        # get dealer hand and pot
        dealerHand = self.data.getTable()
        pot = potValue

        # current highest scoring agents
        highestScoreAgents = ClassicGameRules.determineVictors(self)

        # formatting
        dealerString = "Table\nPot = {}\n--------\n{}\n--------\n".format(pot, handToString(dealerHand))
        playersString = ""
        playersFolded=0
        for i, agentState in enumerate(self.data.agentStates):
            money = agentState.getMoney()
            hand = agentState.getHand()
            handScore = ClassicGameRules.evaluateHand(hand)
            hasFolded = agentState.getHasFolded()
            header=""
            earnings = 0
            if hasFolded:
                header = "-PLAYER FOLDED-"
                playersFolded += 1
            if agentState in highestScoreAgents:
                earnings = potValue/len(highestScoreAgents)
                if agentState.index == highestScoreAgents[0].index:
                    earnings += potValue%len(highestScoreAgents)
                header += "[WINNER, EARNINGS {}] ".format(earnings)
            header += "[MOST RECENT BET {}] ".format(agentState.getBet())
            playersString += header + "[SCORE {}] Player {}\nMoney = {}\nHand: {}  {}\n--------\n".format(handScore, i, money, hand[0], hand[1])
        # let's print it
        if playersFolded == len(self.data.agentStates):
            raise Exception("all {} players cannot fold".format(playersFolded))
        print(dealerString + "{} players folded this round\n-----\n".format(playersFolded) + playersString)

    def updateCall(self, amount):
        self.data.updateCall(amount)

    def mustAnte(self):
        self.data.mustAnte = True

    def anteMet(self):
        self.data.mustAnte = False

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
        agentStates = ClassicGameRules.determineVictors(self)
        if len(agentStates) == 1:
            agentStates[0].addMoney(self.data.getPot())
        else:
            # split pot if it's a tie
            for i in range(len(agentStates)):
                if self.data.getPot() % len(agentStates) != 0:
                    agentStates[i].addMoney(self.data.getPot()/len(agentStates))
                    # naively just give the total remainder to the first person
                    if i == 0:
                        agentStates[i].addMoney(self.data.getPot() % len(agentStates))
                else:
                    agentStates[i].addMoney(self.data.getPot()/len(agentStates))

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
            # print("getting player legal actions")
            return PlayerRules.getLegalActions(self)
        else:
            # print("getting opponent legal actions")
            return OpponentRules.getLegalActions(self, agentIndex)

    def generateSuccessor(self, agentIndex, action):
        if self.isWin() or self.isLose(): raise Exception("Can\'t generate a successor for a terminal state")

        state = GameState(self)

        if agentIndex == 0:
            # print("generating player successor")
            PlayerRules.applyAction(state, action)
        else:
            # print("generating opponent successor")
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
            # print("{} selected action: {}. Remaining Money: {}. Bet: {}".format(agentIndex, action, self.state.data.agentStates[agentIndex].getMoney(), self.state.data.agentStates[agentIndex].getBet()))
            # Change the display
            # self.display.update( self.state.data )
            ###idx = agentIndex - agentIndex % 2 + 1
            ###self.display.update( self.state.makeObservation(idx).data )

            # Track progress
            if agentIndex == numAgents - 1:
                self.numMoves += 1
                self.state.anteMet()
                self.state.roundComplete(True)
                # all players have either called or folded
                for a in self.state.data.agentStates:
                    if not (a.getHasFolded() or self.state.playerHasCalled(a.index)):
                        # print("called {}, folded {}, round continues".format(a.hasFolded, self.state.playerHasCalled(a.index)))
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
