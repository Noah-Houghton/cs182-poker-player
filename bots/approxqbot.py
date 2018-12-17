from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
from pypokerengine.utils.game_state_utils import _restore_table
from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.api.emulator import Emulator
import numpy as np
import time
import random as rand
import util
import math

class ApproxQBot(BasePokerPlayer):

    def __init__(self):
        super(ApproxQBot, self).__init__()
        self.weights = util.Counter()
        self.epsilon = .2
        self.alpha = .6
        self.discount = 1
        self.roundWins = 0
        self.roundLosses = 0
        self.hand = None
        self.pot = 0
        self.latestAction = None
        self.latestBet = 0
        self.currentMoney = 0
        self.currentInvestment = 0
        self.haveActed = False
        self.last_round_state = None
        self.curCC = None


    def getLegalActions(self, round_state):
        table = _restore_table(round_state)
        players = table.seats.players
        return ActionChecker.legal_actions(players, 0, round_state["small_blind_amount"])


    def getFeatures(self, state, action):
        feats = util.Counter()


        feats["hand-strength"] = math.log(state[0])

        # some feature that makes reference to which action you're taking... maybe new pot size?

        # feats["relative-cost-to-play"] = -([action]["amount"])/(self.currentMoney)
        # use ActionChecker.something to get this...
        # might help avoid bust

        # table = _restore_table(state[1])
        # players = table.seats.players
        # all_histories = [p.action_histories for p in players]
        # all_histories = reduce(lambda acc, e: acc + e, all_histories)  # flatten
        # raise_histories = [h for h in all_histories if h["action"] in ["RAISE", "SMALLBLIND", "BIGBLIND"]]
        # feats["opp-confidence"] = (len(raise_histories))/(len(players) - 1)

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
        newCC = gen_cards(round_state['community_card'])
        cur_strength = HandEvaluator.eval_hand(self.hand, self.curCC)
        new_strength = HandEvaluator.eval_hand(self.hand, newCC)
        if self.haveActed:
            self.update((cur_strength, self.last_round_state), self.latestAction, (new_strength, round_state), 10)
        choice = self.getAction((new_strength, round_state), valid_actions)
        action = choice["action"]
        amount = choice["amount"]
        if action == 'raise':
            # naively choose a random raise amt between min and max
            amount = rand.randrange(amount["min"], max(amount["min"], amount["max"]) + 1)
        self.latestAction = action
        self.latestBet = amount
        self.currentInvestment += self.latestBet
        self.last_round_state = round_state
        self.curCC = newCC
        self.haveActed = True
        return action, amount

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hand = gen_cards(hole_card)
        self.currentInvestment = 0
        self.curCC = []
        self.pot = 0
        self.seats = seats
        self.haveActed = False

    def receive_street_start_message(self, street, round_state):            
        self.pot = round_state['pot']['main']['amount']
        self.currentMoney = [s["stack"] for s in round_state["seats"] if s["uuid"] == self.uuid][0]

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.roundWins += int(is_winner)
        self.roundLosses += int(not is_winner)
        reward = 0
        agentWon = [winner["stack"] for winner in winners if winner["uuid"] == self.uuid]
        if is_winner:
            reward = (agentWon[0] - self.currentMoney)
        else:
            reward = (-1 * self.currentInvestment)/10.0
        self.update((HandEvaluator.eval_hand(self.hand, self.curCC), round_state), self.latestAction, None, reward)

def setup_ai():
    return ApproxQBot()
