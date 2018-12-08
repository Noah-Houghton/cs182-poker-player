import rules
import util
import agents
import random


class PokerRules:
    def isRoundOver(self):
        return len(self.dealer.table) == 5
    pass

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
        self._lose = False
        self._win = False
        self._isHandEnd = False
        self._isRoundEnd = False
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


    def getLegalActions(self, agentIndex):
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
class Game:

    def __init__(self, agents, rules=PokerRules()):
        self.rules = rules
        self.agents = agents
        self.startingIndex = 0
        self.gameOver = False
        self.handComplete = False
        self.roundComplete = False
    """
    Play until one player wins as defined by rules.isWin()
    """
    def playFullGame(self):
        # for i in range(len(self.agents)):
        #     agent = self.agents[i]
        #     agent.registerInitialState(self.state.deepCopy())
        agentIndex = self.startingIndex
        numAgents = len( self.agents )
        while not self.gameOver:
            # get agent
            agent = self.agents[agentIndex]
            # get current state
            observation = self.state.deepCopy()
            # solicit an action
            action = agent.getAction(observation)
            self.state = self.state.generateSuccessor( agentIndex, action )
            self.rules.process(self.state, self)
            agentIndex = ( agentIndex + 1 ) % numAgents
        print("Game complete!")
    # """
    # Play a single hand.
    # """
    # def playHand(self):
    #     # for i in range(len(self.agents)):
    #     #     agent = self.agents[i]
    #     #     agent.registerInitialState(self.state.deepCopy())
    #     agentIndex = self.startingIndex
    #     numAgents = len( self.agents )
    #     while not self.handComplete:
    #         # get agent
    #         agent = self.agents[agentIndex]
    #         # get current state
    #         observation = self.state.deepCopy()
    #         # solicit an action
    #         action = agent.getAction(observation)
    #         self.state = self.state.generateSuccessor( agentIndex, action )
    #         self.rules.process(self.state, self)
    #         agentIndex = ( agentIndex + 1 ) % numAgents
    #     print("hand complete!")
    # """
    # Play a single round which begins with the first ante and ends when all players have
    # either called or folded
    # """
    # def playRound(self):
    #     # for i in range(len(self.agents)):
    #     #     agent = self.agents[i]
    #     #     agent.registerInitialState(self.state.deepCopy())
    #     agentIndex = self.startingIndex
    #     numAgents = len( self.agents )
    #     while not self.roundComplete:
    #         # get agent
    #         agent = self.agents[agentIndex]
    #         # get current state
    #         observation = self.state.deepCopy()
    #         # solicit an action
    #         action = agent.getAction(observation)
    #         self.state = self.state.generateSuccessor( agentIndex, action )
    #         self.rules.process(self.state, self)
    #         agentIndex = ( agentIndex + 1 ) % numAgents
    #     print("round complete!")
