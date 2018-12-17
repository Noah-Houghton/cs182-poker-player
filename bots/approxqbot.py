from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import numpy as np
import time
import random as rand
import util
import math

class ApproxQBot(BasePokerPlayer):

    def __init__(self):
        super(ApproxQBot, self).__init__()
        self.weights = util.Counter()
        self.epsilon = .3
        self.alpha = .6
        self.discount = 1
        self.roundWins = 0
        self.roundLosses = 0
        self.hand = None
        self.pot = 0
        self.cc = None
        self.latestAction = None
        self.latestBet = 0
        self.currentMoney = 0
        self.currentInvestment = 0


    def getLegalActions(self, round_state):
        street = round_state["street"]
        min_raise = 0
        if street in round_state["action_histories"].keys():
            moves = round_state["action_histories"][street]
            for move in moves:
                if move["amount"] > min_raise:
                    min_raise = move["amount"]
        min_raise = max(round_state["small_blind_amount"], (min_raise - self.latestBet)) # min raise - last bet
        max_raise = self.seats[0]["stack"]
        if max_raise < min_raise:
            min_raise = max_raise = -1
        return [
            { "action" : "fold" , "amount" : 0 },
            { "action" : "call" , "amount" : min_raise},
            { "action" : "raise", "amount" : { "min": (min_raise + 1), "max": max_raise } }
        ]

    def getFeatures(self, state, action):
        feats = util.Counter()


        feats["hand-strength"] = math.log(HandEvaluator.eval_hand(self.hand, self.cc))

        

        # how many times opponent's have raised 
        # street = round_state["street"]
        # opp_raises = 0
        # if street in round_state["action_histories"].keys():
        #     moves = round_state["action_histories"][street]
        #     for move in moves:
        #         if move[]

        # feats[""] = 

        # feats[""] = state[1]

        # feats[""] = 

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
        next_max_qval = 0
        if nextState != None:
            next_max_qval = self.computeValueFromQValues(nextState, self.getLegalActions(state[1]))
        featureVector = self.getFeatures(state, action).iteritems()
        difference = reward + (self.discount * next_max_qval) - self.getQValue(state, action)
        for (feature, val) in featureVector:
          self.weights[feature] = self.weights[feature] + (self.alpha * difference * val)

    def computeValueFromQValues(self, state, actions):
        if len(actions) == 0:
            return 0.0
        max = float("-inf")
        for action in actions:
            if self.getQValue(state, action["action"]) > max:
                max = self.getQValue(state,action["action"])
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
        self.latestBet = amount
        self.currentInvestment += self.latestBet
        return action, amount

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hand = gen_cards(hole_card)
        self.cc = []
        self.pot = 0
        self.seats = seats

    def receive_street_start_message(self, street, round_state):
        if street != 'preflop':
            self.update( (HandEvaluator.eval_hand(self.hand, self.cc), round_state), self.latestAction,
                (HandEvaluator.eval_hand(self.hand, gen_cards(round_state['community_card'])), round_state['pot']['main']['amount']),
                0)
        self.pot = round_state['pot']['main']['amount']
        self.cc = gen_cards(round_state['community_card'])
        self.currentMoney = self.currentMoney = [s["stack"] for s in round_state["seats"] if s["uuid"] == self.uuid][0]

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.roundWins += int(is_winner)
        self.roundLosses += int(not is_winner)
        reward = 0
        agentWon = [winner["stack"] for winner in winners if winner["uuid"] == self.uuid]
        if is_winner:
            # get amount of money the agent gained by winning this round (?)
            reward = (agentWon[0] - self.currentMoney)/10
            # print("Agent won {}".format(reward))
        else:
            # print("Agent lost")
            reward = (-1 * self.currentInvestment)/10
        self.update((HandEvaluator.eval_hand(self.hand, self.cc), round_state), self.latestAction, None, reward)

def setup_ai():
    return ApproxQBot()
