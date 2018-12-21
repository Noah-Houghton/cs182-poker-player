from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
from pypokerengine.utils.game_state_utils import _restore_table
from pypokerengine.engine.action_checker import ActionChecker
import numpy as np
import time
import random as rand
import util
import math
import os, sys
import dill

bot = os.path.basename(__file__)[:-4]
path = os.path.dirname(os.path.abspath(__file__))
VALUESFILE = path + "/saved_values/" + bot + "_vals.dill"

class ApproxQBot(BasePokerPlayer):

    def __init__(self):
        super(ApproxQBot, self).__init__()
        self.weights = util.Counter()
        self.epsilon = .3
        self.alpha = .2
        self.discount = .9
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
        self.doUpdate = True
        self.SAVEVALS = True

    def saveValues(self):
        with open(VALUESFILE, 'w+') as f:
            dill.dump(self.weights, f)

    def attemptLoadVals(self):
        if not self.weights == {}:
            try:
                with open(VALUESFILE, 'r+') as f:
                    self.weights = dill.load(f)
            except Exception as exception:
                print(exception)
                pass

    def getLegalActions(self, round_state):
        table = _restore_table(round_state)
        players = table.seats.players
        return ActionChecker.legal_actions(players, 0, round_state["small_blind_amount"])


    def getFeatures(self, state, action):
        feats = util.Counter()

        feats["hand-strength"] = 0
        if action["action"] != "fold":
            feats["hand-strength"] = math.log(state[0])/100.0

        # feats["opp-confidence"] = 0
        # if action["action"] != "fold":
        #     streets = state[1]["action_histories"]
        #     confidence = 0
        #     for street in streets:
        #         for act in streets[street]:
        #             if act["uuid"] != self.uuid:
        #                 if act["action"] == "RAISE" :
        #                     confidence += 5
        #                 elif act["action"] == "CALL":
        #                     confidence += 1
        #     feats["opp-confidence"] = float(confidence)/100.0


        #feats["money-left"] = float([s["stack"] for s in state[1]["seats"] if s["uuid"] == self.uuid][0])/100.0

        # feats["relative-cost-to-play"] = 0
        # if action["action"] != "fold":
        #     cost_to_play = 0
        #     for street in streets:
        #         if street == state[1]["street"]:
        #             for act in streets[street]:
        #                 if act["amount"] > cost_to_play :
        #                     cost_to_play = act["amount"]
        #     player_money = [s["stack"] for s in state[1]["seats"] if s["uuid"] == self.uuid][0]
        #     if player_money > 0:
        #         feats["relative-cost-to-play"] = (float(cost_to_play)/float(player_money))*10.0
        feats.divideAll(10.0)
        return feats

    def getQValue(self, state, action):
        featureVector = self.getFeatures(state, action)
        sum = 0
        for feature in featureVector:
            sum = sum + (featureVector[feature] * self.weights[feature])
        # print sum
        return sum

    def update(self, state, action, nextState, reward):
        if self.doUpdate:
            next_max_qval = 0
            if nextState != None:
                next_max_qval = self.computeValueFromQValues(nextState, self.getLegalActions(nextState[1]))
            featureVector = self.getFeatures(state, action).iteritems()
            difference = (reward + (self.discount * next_max_qval)) - self.getQValue(state, action)
            for (feature, val) in featureVector:
                self.weights[feature] =  self.weights[feature] + (self.alpha * difference * val)

    def computeValueFromQValues(self, state, actions):
        if len(actions) == 0:
            return 0.0
        max_val = float("-inf")
        for action in actions:
            if self.getQValue(state, action) > max_val:
                max_val = self.getQValue(state,action)
        return max_val

    def computeActionFromQValues(self, state, actions):
        if len(actions) == 0:
            return None
        max_val = float("-inf")
        maxAction = {'action': 'fold', 'amount': 0}
        for action in actions:
            if self.getQValue(state, action) == max_val:
                max_val = self.getQValue(state, action)
                maxAction = action
            elif self.getQValue(state, action) > max_val:
                max_val = self.getQValue(state, action)
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
            self.update((cur_strength, self.last_round_state), self.latestAction, (new_strength, round_state), 0)
        choice = self.getAction((new_strength, round_state), valid_actions)
        action = choice["action"]
        amount = choice["amount"]
        if isinstance(amount, dict):
            min_val = amount["min"]
            max_val = amount["max"]
            amount = choice["amount"] = rand.randrange(min_val, max_val + 1)
        self.latestAction = choice
        self.latestBet = amount
        self.currentInvestment += self.latestBet
        self.last_round_state = round_state
        self.curCC = newCC
        self.haveActed = True
        # print action
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
        self.latestAction = None
        self.latestBet = 0

    def receive_street_start_message(self, street, round_state):
        self.pot = round_state['pot']['main']['amount']
        self.currentMoney = [s["stack"] for s in round_state["seats"] if s["uuid"] == self.uuid][0]

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.roundWins += int(is_winner)
        self.roundLosses += int(not is_winner)
        self.alpha = self.alpha
        reward = 0
        hand_strength = HandEvaluator.eval_hand(self.hand, self.curCC)
        agentWon = [winner["stack"] for winner in winners if winner["uuid"] == self.uuid]
        if is_winner:
            reward = math.log((agentWon[0] - self.currentMoney)) * 1.2
        elif self.currentInvestment > 0:
            reward = math.log(self.currentInvestment) * -1.0
        # elif self.currentMoney == 0:
        #     reward = -10
        if self.haveActed:
            self.update((hand_strength, round_state), self.latestAction, None, reward)

def setup_ai():
    bot = ApproxQBot()
    if bot.SAVEVALS:
        bot.attemptLoadVals()
    return bot
