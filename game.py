"""Defines a series of functions to fully simulate a game of poker"""

import random as rand

suits = ["Diamonds", "Hearts", "Spades", "Clubs"]
acceptedValues = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
legalActions = ["Call", "Raise", "Fold", "All-in", "Double Down"]
hands = {"Royal Flush": 32, "Straight Flush": 31, "Four of a Kind": 30, "Full House": 29, "Flush": 28, "Straight": 27, "Three of a Kind": 26, "Two Pair": 25, "Pair" : 24}
names = ["John", "Alex", "Steve", "Lev"]


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

    def draw(self):
        try:
            card = self.cards.pop()
        # if pop fails, we need to reshuffle the deck
        # this does not take into account cards that players currently have
        except:
            self.__init__()
            card = self.cards.pop()
        return card

    # we may need this for reshuffling?
    def returnToDeck(self, cards):
        self.cards += cards
        self.shuffle()

    # could be useful for special decks and/or proper reshuffling
    def removeFromDeck(self, cards):
        for card in cards:
            self.cards.remove(card)
        self.shuffle()

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
        self.name = rand.choice(names)

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
        return "{} | Hand: {} Cash: {}".format(self.name, self.hand, self.money)

    def __repr__(self):
        return "{} | Hand: {} Cash: {}".format(self.name, self.hand, self.money)

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
            self.players.append(Player(1000, 2, self.decks, self.pot))
        self.actions = legalActions
        # dealer handsize is one less than starting so that it can draw at the beginning of the first round
        self.dealer = Player(0, 2, self.decks, self.pot)
        self.isGameOver = False
        self.ante = 1

    def newDecks(self, decks):
        self.decks = decks

    def isStraightFlush(self, hand):
        lastVal = None
        for card in hand:
            if lastVal == None:
                lastVal = card.value
                pass
            # TODO: Ace can be 1 or 14
            if card.value == lastVal + 1:
                lastVal = card.value
            else:
                return False
        return True

    def handToScore(self, hand):
        """Given a player's hand, returns the highest point score they can make."""
        scoringCards = hand + self.dealer.hand
        hearts = [card for card in scoringCards if card.suit == "Hearts"]
        diamonds = [card for card in scoringCards if card.suit == "Diamonds"]
        spades = [card for card in scoringCards if card.suit == "Spades"]
        clubs = [card for card in scoringCards if card.suit == "Clubs"]
        scoringSuits = [hearts, diamonds, spades, clubs]
        for s in scoringSuits:
            if len(s) == 0:
                scoringSuits.remove(s)

        ranks = []
        for value in acceptedValues:
            ranks.append([card for card in scoringCards if card.value == value])
        bestHand = 0
        for suit in scoringSuits:
            royalFlush = [PlayingCard(suit[0].suit, 1), PlayingCard(suit[0].suit, 13), PlayingCard(suit[0].suit, 12), PlayingCard(suit[0].suit, 11), PlayingCard(suit[0].suit, 10)]
            if len(suit) == 5:
                # check for royal/straight flush/flush
                if royalFlush.sort() is suit.sort():
                    if bestHand < hands["Royal Flush"]:
                        bestHand = hands["Royal Flush"]
                elif self.isStraightFlush(scoringCards):
                    if bestHand < hands["Straight Flush"]:
                        bestHand = hands["Straight Flush"]
                else:
                    if bestHand < hands["Flush"]:
                        bestHand = hands["Flush"]
        threeOfAKind = False
        pair = False
        for rank in ranks:
            if len(rank) == 4:
                # four of a kind
                if bestHand < hands["Four of a Kind"]:
                    bestHand = hands["Four of a Kind"]
            if len(rank) == 3:
                # three of a kind, or full house
                if pair:
                    if bestHand < hands["Full House"]:
                        bestHand = hands["Full House"]
                threeOfAKind = True
                if bestHand < hands["Three of a Kind"]:
                    bestHand = hands["Three of a Kind"]
            if len(rank) == 2:
                # pair
                if threeOfAKind:
                    if bestHand < hands["Full House"]:
                        bestHand = hands["Full House"]
                if pair:
                    if bestHand < hands["Two Pair"]:
                        bestHand = hands["Two Pair"]
                else:
                    pair = True
                    if bestHand < hands["Pair"]:
                        bestHand = hands["Pair"]
        if bestHand == 0:
            bestHand = max([x.value for x in hand])
        return bestHand

    def declareWinner(self, players):
        """Given a list of players, compares their hands against each other
        (taking into account the dealer's cards) to determine the winner(s)
        of the hand. Returns a list of winning players."""
        if len(players) == 1:
            return [players[0]]
        scores = []
        for player in players:
            scores.append((self.handToScore(player.hand + self.dealer.hand), player))
        # TODO: enforce suit precedence
        return [player for score, player in scores if score == max(scores)]

    def getRichestPlayer(self):
        richest = None
        mostMoney = float("-inf")
        for player in self.players:
            if player.money > mostMoney:
                mostMoney = player.money
                richest = player
        return player

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
            # # players receive cards
            # for player in self.players:
            #     player.draw()
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
                    if player.money < callVal or player.money == 0:
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
        if not self.isGameOver:
            # new dealer hand
            self.dealer.newHand()
            # new player hands
            for player in self.players:
                player.newHand()

    def playGame(self):
        while not self.isGameOver:
            self.playHand()
        print("game complete! {} won.".format(self.getRichestPlayer()))


if __name__ == "__main__":
    for _ in range(5):
        game = Poker(3, [Deck()])
        game.playGame()
