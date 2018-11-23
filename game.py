"""Defines a series of functions to fully simulate a game of poker"""

import random as rand

suits = {"Diamonds": 1, "Hearts": 2, "Spades": 3, "Clubs": 4}
acceptedValues = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
legalActions = ["Call", "Raise", "Fold", "All-in", "Double Down"]

class PlayingCard:

    def __init__(self, suit, value):
        if suit not in suits or value not in acceptedValues:
            return ValueError
        self.suit = suit
        self.value = value

    def getValue(self):
        return self.value

    def getSuit(self):
        return self.suit

    def __str__(self):
        if self.value == 13:
            return "{} of {}".format("King", self.suit)
        if self.value == 12:
            return "{} of {}".format("Queen", self.suit)
        if self.value == 11:
            return "{} of {}".format("Jack", self.suit)
        if self.value == 1:
            return "{} of {}".format("Ace", self.suit)
        else:
            return "{} of {}".format(self.value, self.suit)

    def __repr__(self):
        if self.value == 13:
            return "{} of {}".format("King", self.suit)
        if self.value == 12:
            return "{} of {}".format("Queen", self.suit)
        if self.value == 11:
            return "{} of {}".format("Jack", self.suit)
        if self.value == 1:
            return "{} of {}".format("Ace", self.suit)
        else:
            return "{} of {}".format(self.value, self.suit)

class Deck:

    def __init__(self, vals=acceptedValues, suits=suits):
        self.cards = []
        for val in vals:
            for suit in suits:
                self.cards.append(PlayingCard(suit, val))
        self.shuffle()

    # TODO: deal with decks running out of cards
    def draw(self):
        return self.cards.pop()

    def shuffle(self):
        rand.shuffle(self.cards)

    def __str__(self):
        return str(self.cards)

    def __repr__(self):
        return str(self.cards)


class Player:

    def __init__(self, startingMoney, sizeHand, sourceDecks, pot):
        self.sizeHand = sizeHand
        self.money = startingMoney
        self.sourceDecks = sourceDecks
        self.pot = pot
        self.hand = []
        self.isWinner = False
        self.newHand()

    def bet(self, val):
        if val > self.money:
            return ValueError
        self.money -= val
        self.pot.payIn(val)

    def receivePayOut(self, val):
        self.money += val

    def draw(self):
        deck = rand.choice(self.sourceDecks)
        self.hand.append(deck.draw())

    def newHand(self):
        self.hand = []
        while len(self.hand) < self.sizeHand:
            deck = rand.choice(self.sourceDecks)
            self.hand.append(deck.draw())

    def __str__(self):
        return "Player hand: {}\nPlayer cash: {}".format(self.hand, self.money)

    def __repr__(self):
        return "Player hand: {}\nPlayer cash: {}".format(self.hand, self.money)

class Pot:

    def __init__(self):
        self.dollars = 0

    def payIn(self, val):
        self.dollars += val

    def payOut(self, players):
        for player in players:
            player.receivePayOut(self.dollars / len(players))
        self.dollars = 0

    def __str__(self):
        return "{} in the pot".format(self.dollars)

class Poker:

    def __init__(self, numPlayers, decks):
        self.pot = Pot()
        self.decks = decks
        self.players = []
        for _ in range(numPlayers):
            self.players.append(Player(1000, 7, self.decks, self.pot))
        self.actions = legalActions
        # dealer handsize is one less than starting so that it can draw at the beginning of the first round
        self.dealer = Player(0, 1, self.decks, self.pot)
        self.isGameOver = False
        self.ante = 1

    def declareWinner(self, players):
        """Given a list of players, compares their hands against each other
        (taking into account the dealer's cards) to determine the winner(s)
        of the hand."""
        # TODO
        return players
        pass

    def playHand(self):
        handComplete = False
        while not handComplete:
            # at the start of the round, let's see if anyone has won or lost
            for player in self.players:
                if player.money <= 0:
                    self.players.remove(player)
                    if len(self.players) == 1:
                        self.players[0].isWinner = True
                        self.isGameOver = True
            roundComplete = False
            roundPlayers = list(self.players)
            # dealer draws
            self.dealer.draw()
            # if the dealer is done drawing, declare winners and start new round
            if len(self.dealer.hand) > 5 or len(roundPlayers) == 1:
                self.winningPlayers = self.declareWinner(roundPlayers)
                handComplete = True
            # players receive cards
            for player in self.players:
                player.draw()
            # expose dealer's hand to the players for their decision-making
            dealerHand = self.dealer.hand
            # players decide to take an action based on the available information
            callVal = self.ante
            roundComplete = False
            while not roundComplete:
                roundComplete = True
                if len(roundPlayers) == 1:
                    break
                for player in roundPlayers:
                    # for each player, select an action based on our agent
                    # the round doesn't end until everyone has called or folded

                    # TODO
                    action = rand.choice(legalActions)
                    # if a player cannot at least call, they must fold
                    if player.money < callVal:
                        action = "Fold"
                    if action == "Call":
                        player.bet(callVal)
                    if action == "Raise":
                        amtRaise = 1
                        player.bet(callVal + amtRaise)
                        callVal += amtRaise
                        roundComplete = False
                    if action == "Double down":
                        player.bet(callVal * 2)
                        callVal = callVal * 2
                        roundComplete = False
                    if action == "All-in":
                        player.bet(player.money)
                        callVal = player.money
                        roundComplete = False
                    if action == "Fold":
                        roundPlayers.remove(player)

        # payout if we're done with the hand
        winners = self.winningPlayers
        self.pot.payOut(winners)
        print(winners)
        if not self.isGameOver:
            # new dealer hand
            self.dealer.newHand()
            # new player hands
            for player in self.players:
                player.newHand()

    def playGame(self):
        while not self.isGameOver:
            self.playHand()
        print("game complete!")


if __name__ == "__main__":
    game = Poker(3, [Deck()])
    game.playGame()
