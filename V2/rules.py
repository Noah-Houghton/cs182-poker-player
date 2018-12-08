"""
Common set of functions for rules
"""
class Rules:

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

    def applyAction(self, state, action):
        pass

    def process(self, state, game):
        pass


"""
Defines a set of rules by which the opponents operate
"""
class OpponentRules(Rules):
    def getLegalActions(self, agentIndex):
        pass

    def applyAction(self, state, action, agentIndex):
        pass

    def process(self, state, game):
        pass
