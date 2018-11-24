"""Defines a series of functions to fully simulate a game of poker"""

import random as rand

suits = ["Diamonds", "Hearts", "Spades", "Clubs"]
acceptedValues = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
legalActions = ["Call", "Raise", "Fold", "All-in", "Double Down"]
hands = {"Royal Flush": 32, "Straight Flush": 31, "Four of a Kind": 30, "Full House": 29, "Flush": 28, "Straight": 27, "Three of a Kind": 26, "Two Pair": 25, "Pair" : 24}
names = ["John", "Alex", "Steve", "Lev", "Herbie", "David", "Eve", "Alyx"]


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

    def __gt__(self, card2):
        return self.value < card2.value
    def __lt__(self, card2):
        return self.value < card2.value

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

    def __init__(self, startingMoney, sizeHand, sourceDecks):
        self.sizeHand = sizeHand
        self.money = startingMoney
        self.startingMoney = startingMoney
        self.sourceDecks = sourceDecks
        self.hand = []
        self.isWinner = False
        self.newHand()
        self.name = "default"
        self.hasFolded = False

    def reset(self):
        self.money = self.startingMoney
        self.hasFolded = False

    def bet(self, val, pot):
        if val > self.money:
            return ValueError
        self.money -= val
        pot.payIn(val)

    def receivePayOut(self, val):
        self.money += val

    def draw(self):
        deck = rand.choice(self.sourceDecks)
        self.hand.append(deck.draw())

    def newHand(self):
        self.hand = []
        for _ in range(self.sizeHand):
            self.draw()

    def newDecks(self, decks):
        self.sourceDecks = decks

    def __str__(self):
        return "{} | Hand: {} Cash: {}".format(self.name, self.hand, self.money)

    def __repr__(self):
        return "{} | Hand: {} Cash: {}".format(self.name, self.hand, self.money)

    def __gt__(self, player2):
        return self.money > player2.money

    def __ge__(self, player2):
        return self.money >= player2.money

    def __lt__(self, player2):
        return self.money < player2.money

    def __le__(self, player2):
        return self.money <= player2.money

class Pot:

    def __init__(self):
        self.dollars = 0

    def payIn(self, val):
        self.dollars += val

    def payOut(self, players):
        payout = self.dollars / len(players)
        for player in players:
            player.receivePayOut(payout)
        self.dollars = 0

    def __str__(self):
        return "{} in the pot".format(self.dollars)

class Poker:

    def __init__(self, decks, numPlayers=0, startingPlayers=[]):
        self.pot = Pot()
        self.decks = decks
        self.actions = legalActions
        # dealer handsize is one less than starting so that it can draw at the beginning of the first round
        self.dealer = Player(0, 2, self.decks)
        self.isGameOver = False
        self.ante = 1
        self.players = startingPlayers
        self.initPlayers(numPlayers)

    def newDecks(self, decks, bNewHands=False):
        self.decks = decks
        for player in self.players:
            player.newDecks(decks)
        self.dealer.newDecks(decks)
        if bNewHands:
            self.forceNewHands()

    def forceNewHands(self):
        for player in self.players:
            player.newHand()
        self.dealer.newHand()

    def initPlayers(self, numPlayers):
        newPlayers = []
        for _ in range(numPlayers):
            newPlayers.append(Player(1000, 2, self.decks))
        sample = rand.sample(names, len(newPlayers))
        for i, player in enumerate(newPlayers):
            player.name = sample[i]
        self.players += newPlayers

    def newDecks(self, decks):
        self.decks = decks

    def isStraightFlush(self, hand):
        lastVal = None
        hand.sort()
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

    def handToScore(self, hand, dealerHand):
        """Given a player's hand, returns the highest point score they can make."""
        scoringCards = hand + dealerHand
        hearts = [card for card in scoringCards if card.suit == "Hearts"]
        diamonds = [card for card in scoringCards if card.suit == "Diamonds"]
        spades = [card for card in scoringCards if card.suit == "Spades"]
        clubs = [card for card in scoringCards if card.suit == "Clubs"]
        scoringSuits = [x for x in [hearts, diamonds, spades, clubs] if x != []]
        ranks = []
        for value in acceptedValues:
            ranks.append([card for card in scoringCards if card.value == value])
        ranks = [x for x in ranks if x != []]
        bestHand = 0
        for suit in scoringSuits:
            royalFlush = [PlayingCard(suit[0].suit, 1), PlayingCard(suit[0].suit, 13), PlayingCard(suit[0].suit, 12), PlayingCard(suit[0].suit, 11), PlayingCard(suit[0].suit, 10)]
            if len(suit) == 5:
                # check for royal/straight flush/flush
                if royalFlush.sort() == suit.sort():
                    if bestHand < hands["Royal Flush"]:
                        bestHand = hands["Royal Flush"]
                elif self.isStraightFlush(suit):
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
        """Given a list of players, compares their hands against each other to
        determine the winner(s) of the hand. Returns a list of winning players."""
        scores = []
        for player in players:
            scores.append((self.handToScore(player.hand, self.dealer.hand), player))
        # TODO: enforce suit precedence
        allScores = [x for x,_ in scores]
        return [player for score, player in scores if score == max(allScores)]

    def getRichestPlayer(self):
        return max(self.players)

    def playRound(self):
        self.dealer.draw()
        callVal = self.ante
        roundComplete = False
        while not roundComplete:
            roundComplete = True
            for player in self.players:
                # if only one player has not folded, that person wins the round
                if len([x for x in self.players if not x.hasFolded]) == 1:
                    break
                # for each player, select an action based on our agent
                # the round doesn't end until everyone has called or folded
                if player.hasFolded:
                    pass
                # TODO
                action = rand.choice(["Call", "Raise"])
                # if a player cannot at least call, they must fold
                if player.money < callVal or player.money == 0:
                    action = "Fold"
                if action == "Call":
                    player.bet(callVal, self.pot)
                if action == "Raise":
                    amtRaise = 10
                    player.bet(callVal + amtRaise, self.pot)
                    callVal += amtRaise
                    roundComplete = False
                if action == "Double down":
                    player.bet(callVal * 2, self.pot)
                    callVal = callVal * 2
                    roundComplete = False
                if action == "All-in":
                    player.bet(player.money, self.pot)
                    callVal = player.money
                    roundComplete = False
                if action == "Fold":
                    player.hasFolded = True
                # print("{} has taken action {} at callVal {}".format(player, action, callVal))


    def playHand(self):
        # hand is over when dealer hand is 5
        while not len(self.dealer.hand) == 5:
            # players decide to take an action based on the available information
            self.playRound()
        # payout if we're done with the hand
        winners = self.declareWinner([x for x in self.players if not x.hasFolded])
        self.pot.payOut(winners)
        # print("{} won the hand".format(winners))
        self.ante = 1
        for player in self.players:
            player.hasFolded = False
        # at the end of the round, let's see if anyone has won, i.e. all except one has lost
        # print("players are {}".format(self.players))
        if len([player for player in self.players if player.money == 0]) == len(self.players) - 1:
            self.isGameOver = True


    def playGame(self):
        self.isGameOver = False
        while not self.isGameOver:
            self.playHand()
            self.forceNewHands()
        print("game complete! {} won.".format(self.getRichestPlayer()))
        # reset for next game
        self.ante = 1
        for player in self.players:
            player.reset()

if __name__ == "__main__":
    game = Poker([Deck()], numPlayers=2)
    for _ in range(10):
        game.playGame()
