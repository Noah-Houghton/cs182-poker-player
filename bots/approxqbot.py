from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import numpy as np
import time
import random as rand
import util

def adjusted_montecarlo_simulation(nb_player, hole_card, community_card):
    # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
    community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
    unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
    opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
    opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
    my_score = HandEvaluator.eval_hand(hole_card, community_card)
    return my_score / max(opponents_score)


class ApproxQBot(BasePokerPlayer):

    def __init__(self):
        super(ApproxQBot, self).__init__()
        self.weights = util.Counter()
        self.epsilon = .1
        self.alpha = .3
        self.discount = 0
        self.roundWins = 0
        self.roundLosses = 0
        self.hand = None
        self.pot = 0
        self.cc = None
        self.latestAction = None

    def getFeatures(self, state, action):
        feats = util.Counter()

        feats["hand-strength"] = state[0]
        # feats["num-players-in"] = state[1]
        # feats["player-money"] = state[2]
        # feats["price-to-play"] = state[3]
        # feats["pot-size"] = state[4]

        feats.divideAll(10.0)
        return feats

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        featureVector = self.getFeatures(state, action)
        sum = 0
        for feature in featureVector:
          sum = sum + (featureVector[feature] * self.weights[feature])
        return sum

    def update(self, state, action, nextState, reward):
        next_max_qval = self.computeValueFromQValues(nextState, )
        featureVector = self.getFeatures(state, action).iteritems()
        difference = reward + (self.discount * next_max_qval) - self.getQValue(state, action)
        for (feature, val) in featureVector:
          self.weights[feature] = self.weights[feature] + (self.alpha * difference * val)

    def computeValueFromQValues(self, state, actions):
        if len(actions) == 0:
            return 0.0
        max = float("-inf")
        for action in actions:
            if self.getQValue(state, action) > max:
                max = self.getQValue(state,action)
        return max

    def computeActionFromQValues(self, state, actions):
        if len(actions) == 0:
            return None
        max = float("-inf")
        maxAction = {'action': 'fold', 'amount': 0}
        for action in actions:
            if self.getQValue(state, action["action"]) == max:
                max = self.getQValue(state, action["action"])
                maxAction = action
            elif self.getQValue(state, action["action"]) > max:
                max = self.getQValue(state, action["action"])
                maxAction = action
        return maxAction

    def getAction(self, state, actions):
        if util.flipCoin(self.epsilon):
            return rand.choice(actions)
        else:
            return self.computeActionFromQValues(state, actions)

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = gen_cards(round_state["community_card"])
        hole_card = gen_cards(hole_card)
        handStrength = HandEvaluator.eval_hand(hole_card, community_card)
        choice = self.getAction((handStrength, round_state["pot"]["main"]["amount"]), valid_actions)
        action = choice["action"]
        amount = choice["amount"]
        if action == 'raise':
            # naively choose a random raise amt between min and max
            amount = rand.randrange(amount["min"], max(amount["min"], amount["max"]) + 1)
        self.latestAction = action
        return action, amount

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hand = gen_cards(hole_card)
        self.cc = []
        self.pot = 0

    def receive_street_start_message(self, street, round_state):
        if street != 'preflop':
            self.update((HandEvaluator.eval_hand(self.hand, self.cc), self.pot), self.latestAction,
                (HandEvaluator.eval_hand(self.hand, gen_cards(round_state['community_card'])), round_state['pot']['main']['amount']),
                adjusted_montecarlo_simulation(self.num_players, self.hand, gen_cards(round_state['community_card'])) * round_state['pot']['main']['amount'])
        self.pot = round_state['pot']['main']['amount']
        self.cc = gen_cards(round_state['community_card'])

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.roundWins += int(is_winner)
        self.roundLosses += int(not is_winner)

def setup_ai():
    return ApproxQBot()
