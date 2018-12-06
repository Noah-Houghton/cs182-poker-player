"""Defines a smart agent which can learn to play poker"""
"""
MDP
We define the set of states in our MDP version of this agent as the cards the player has available to them, the money the player has left, and the money in the pot.
Set of States S:
    -


"""

from game import agent

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
        self.evaluationFunction =
        self.depth = int(depth)
        self.bestAction =


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
