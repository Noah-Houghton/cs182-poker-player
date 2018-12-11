import util
import random
from game import PokerMoves
from game import ClassicGameRules

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
        The Agent will receive a GameState and
        must return an action
        """
        raiseNotDefined()

    # def registerInitialState(self, state):
    #     self.

class OnlyFlushAgent(Agent):
    """
    This agent only bets when it has a flush or better in hand.
    """
    def getAction(self, gameState):
        legalMoves = gameState.getLegalActions(self.index)
        flushes = [ClassicGameRules.FLUSH, ClassicGameRules.STRAIGHTFLUSH, ClassicGameRules.ROYALFLUSH]
        if ClassicGameRules.evaluateHand(gameState.getHandAndTable(self.index)) in flushes:
            if PokerMoves.ALLIN in legalMoves:
                return PokerMoves.ALLIN
            elif PokerMoves.LARGERAISE in legalMoves:
                return PokerMoves.LARGERAISE
            elif PokerMoves.RAISE in legalMoves:
                return PokerMoves.RAISE
            else:
                return random.choice(legalMoves)
        else:
            if PokerMoves.FOLD in legalMoves:
                return PokerMoves.FOLD
            else:
                return random.choice(legalMoves)



class NaiveAgent(Agent):
    """
    Based on pot size, hand strength,
    and money player has, chooses an
    action.

    s = strength hand
    p = pot size
    z = agent money

    if p < 50:
        max = s * (1-1/z)
    else:
        max = 2s * (1-1/z)

    Where max is the player's maximum bet cost
    """
    def getAction(self, gameState):
        handStrength = gameState.getHandStrength(self.index)
        potSize = gameState.getPot()
        agentMoney = gameState.data.agentStates[self.index].getMoney()
        maxBet = 0
        if agentMoney > 0:
            if potSize > 50:
                maxBet = handStrength * (1 - (1.0/agentMoney))
            else:
                maxBet = handStrength * 2 * (1 - (1.0/agentMoney))
        legalMoves = gameState.getLegalActions(self.index)
        # selects the action whose cost is closest to max
        # as calculated above
        highestCost = float("-inf")
        bestAction = None
        for move in legalMoves:
            # print("checking {}".format(move))
            cost = PokerMoves.moveToCost(move, gameState, self.index)
            if cost > highestCost and cost <= maxBet:
                highestCost = cost
                bestAction = move
        return bestAction


class RandomAgent(Agent):
    """
    Returns a random legal action.
    """
    def getAction(self, gameState):
        legalMoves = gameState.getLegalActions(self.index)
        return random.choice(legalMoves)

class AlwaysCallAgent(Agent):
    """
    Returns Call if it is able, otherwise returns a random legal action.
    """
    def getAction(self, gameState):
        legalMoves = gameState.getLegalActions(self.index)
        if PokerMoves.CALL in legalMoves:
            return PokerMoves.CALL
        else:
            return random.choice(legalMoves)

class AlwaysRaiseAgent(Agent):
    """
    Returns Raise if it is able, otherwise returns a random legal action.
    """
    def getAction(self, gameState):
        legalMoves = gameState.getLegalActions(self.index)
        if PokerMoves.RAISE in legalMoves:
            return PokerMoves.RAISE
        else:
            return random.choice(legalMoves)

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions(self.index)
        # Choose one of the best actions
        if legalMoves == []:
            raise Exception("no  legal moves returned")
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        # print("agent chose {}".format(legalMoves[chosenIndex]))
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePlayerSuccessor(action)

        newMoney = successorGameState.getPlayerMoney()
        newHand = successorGameState.getPlayerHand()

        "*** YOUR CODE HERE ***"
        # gets the score by taking next move
        # score is the money the player has, so this is a bad heuristic
        return successorGameState.getScore()
