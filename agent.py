"""Defines a smart agent which can learn to play poker"""
"""
MDP
We define the set of states in our MDP version of this agent as the cards the player has available to them, the money the player has left, and the money in the pot.
Set of States S:
    - boolean playerInRound
    - float currentBet
    - int numPlayersInRound

Set of Actions A:
    - fold
    - raise
    - call
    - double down
    - all-in

Transitions
    - fold sends players to a terminal state
    - raise increases currentBet
    - call, currentBet remains the same
    - double down, currentBet doubles
    - all-in, currentBet = allMoney
    TODO: how do these transitions affect numPlayersInRound and playerInRound? do they have to?

"""



class Configuration:
    """
    A Configuration holds information about the agent's current status in the game space.
    """

    def __init__(self, hand, money, recentBet):
        self.hand = hand
        self.money = money
        self.bet = recentBet

    def getMoney(self):
        return self.money

    def getHand(self):
        return self.hand

    def getAggression(self):
        return self.aggression

    def __eq__(self, other):
        if other == None: return False
        return (self.hand == other.hand and self.money == other.money)

    def __hash__(self):
        x = hash(self.hand)
        y = hash(self.money)
        return hash(x + 13 * y)

    def __str__(self):

        return "Hand: "+str(self.hand)+"\nCash="+str(self.money)+"\nLatest Bet="+str(self.bet)

    def generateSuccessor(self, bet, card=None):
        """
        Generates a new configuration reached by translating the current
        configuration by the action vector. This is a low-level call and does
        not attempt to respect the legality of the movement.

        Bet is the amount of money the player is betting; card is to be added to the hand, if applicable
        """

        if not card == None: return Configuration(self.hand.addCard(card), self.money - bet, bet)
        return Configuration(self.hand, self.money - bet, bet)

class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    """

    def __init__( self, startConfiguration ):
        self.start = startConfiguration
        self.configuration = startConfiguration

    def __str__( self ):
        return "Player: " + str( self.configuration )

    def __eq__( self, other ):
        if other == None:
            return False
        return self.configuration == other.configuration

    def __hash__(self):
        return hash(hash(self.configuration) + 13 * hash(self.scaredTimer))

    def copy( self ):
        state = AgentState( self.start )
        state.configuration = self.configuration
        return state


    def getHand(self):
        if self.configuration == None: return None
        return self.configuration.getHand()

    def getMoney(self):
        if self.configuration == None: return None
        return self.configuration.getMoney()


class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # inspects the starting state
    """
    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a GameState and must return a poker action.
        """
        raiseNotDefined()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)
        self.bestAction = (float("-inf"), Actions.FOLD)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def minimax(self, gameState, depth, agentID):
        if depth >= self.depth and agentID == self.index or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        # we can do this here because we're not pruning; later stages must generate
        # on request to enable pruning the tree
        successors = [(gameState.generateSuccessor(agentID, action), action) for action in gameState.getLegalActions(agentID)]
        if not len(successors):
            return self.evaluationFunction(gameState)
        if agentID == self.index:
            value = float("-inf")
            for successor in successors:
                value = max(value, self.minimax(successor[0], depth + 1, (agentID + 1) % gameState.getNumAgents()))
                if depth == 0 and value != self.bestAction[0]:
                    self.bestAction = (value, successor[1])
            return value
        else:
            value = float("inf")
            for successor in successors:
                value = min(value, self.minimax(successor[0], depth, (agentID + 1) % gameState.getNumAgents()))
            return value

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        self.minimax(gameState, 0, self.index)
        return self.bestAction[1]

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def AB_minimax(self, gameState, depth, A, B, agentID):
        if depth >= self.depth and agentID == self.index or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        if agentID == self.index:
            value = float("-inf")
            for action in gameState.getLegalActions(agentID):
                value = max(value, self.AB_minimax(gameState.generateSuccessor(agentID, action), depth + 1, A, B, (agentID + 1) % gameState.getNumAgents()))
                if value > B:
                    return value
                if depth == 0 and value != self.bestAction[0]:
                    self.bestAction = (value, action)
                A = max(A, value)
            return value
        else:
            value = float("inf")
            for action in gameState.getLegalActions(agentID):
                value = min(value, self.AB_minimax(gameState.generateSuccessor(agentID, action), depth, A, B, (agentID + 1) % gameState.getNumAgents()))
                if value < A:
                    return value
                B = min(B, value)
            return value

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        self.AB_minimax(gameState, 0, float("-inf"), float("inf"), self.index)
        return self.bestAction[1]
