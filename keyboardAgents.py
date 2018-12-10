from agents import Agent
from game import PokerMoves
import random
import game
import util

class KeyboardAgent(Agent):
    """
    An agent controlled by the keyboard.
    """
    # NOTE: Arrow keys also work.
    WEST_KEY  = 'a'
    EAST_KEY  = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__( self, index = 0 ):

        self.lastMove = PokerMoves.FOLD
        self.index = index
        self.keys = []

    def getAction( self, state):
        from graphicsUtils import keys_waiting
        from graphicsUtils import keys_pressed
        keys = keys_waiting() + keys_pressed()
        if keys != []:
            self.keys = keys

        legal = state.getLegalActions(self.index)
        move = self.getMove(legal)

        if move == PokerMoves.FOLD:
            # Try to move in the same direction as before
            if self.lastMove in legal:
                move = self.lastMove

        if (self.STOP_KEY in self.keys) and PokerMoves.FOLD in legal: move = PokerMoves.FOLD

        if move not in legal:
            move = random.choice(legal)

        self.lastMove = move
        return move

    def getMove(self, legal):
        # todo make this better
        move = PokerMoves.FOLD
        if   (self.WEST_KEY in self.keys or 'Left' in self.keys) and PokerMoves.ALLIN in legal:  move = PokerMoves.ALLIN
        if   (self.EAST_KEY in self.keys or 'Right' in self.keys) and PokerMoves.RAISE in legal: move = PokerMoves.RAISE
        if   (self.NORTH_KEY in self.keys or 'Up' in self.keys) and PokerMoves.CALL in legal:   move = PokerMoves.CALL
        if   (self.SOUTH_KEY in self.keys or 'Down' in self.keys) and PokerMoves.DOUBLEDOWN in legal: move = PokerMoves.DOUBLEDOWN
        return move

class KeyboardAgent2(KeyboardAgent):
    """
    A second agent controlled by the keyboard.
    """
    # NOTE: Arrow keys also work.
    WEST_KEY  = 'j'
    EAST_KEY  = "l"
    NORTH_KEY = 'i'
    SOUTH_KEY = 'k'
    STOP_KEY = 'u'

    def getMove(self, legal):
        move = Directions.STOP
        if   (self.WEST_KEY in self.keys) and Directions.WEST in legal:  move = Directions.WEST
        if   (self.EAST_KEY in self.keys) and Directions.EAST in legal: move = Directions.EAST
        if   (self.NORTH_KEY in self.keys) and Directions.NORTH in legal:   move = Directions.NORTH
        if   (self.SOUTH_KEY in self.keys) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
