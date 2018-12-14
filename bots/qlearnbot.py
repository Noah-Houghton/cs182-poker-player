# from https://www.data-blogger.com/2017/11/01/pokerbot-create-your-poker-ai-bot-in-python/
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import numpy as np
import time
import random
import util



class QLearnBot(BasePokerPlayer):
    def __init__(self):
        super(QLearnBot, self).__init__()
        self.qvalues = util.Counter()
        self.epsilon = .08
        self.alpha = .1
        self.discount = .1
        self.wins = 0
        self.losses = 0

    def getQValue(self, state, action):
        return self.qvalues[(state,action)]

    def computeValueFromQValues(self, state, actions):

        if len(actions) == 0:
            return 0.0

        max = float("-inf")
        for action in actions:
            if self.getQValue(state, action) > max:
                max = self.getQValue(state,action)
        return max

    def computeActionFromQValues(self, state, action):
        if len(actions) == 0:
            return None
        max = float("-inf")
        maxAction = None
        for action in actions:
            if self.getQValue(state, action) == max:
                if util.flipCoin(.5):
                    max = self.getQValue(state,action)
                    maxAction = action
            elif self.getQValue(state,action) > max:
                max = self.getQValue(state,action)
                maxAction = action
        return maxAction

    def getAction(self, state, actions):
        if util.flipCoin(self.epsilon):
            return random.choice(actions)
        else:
            return self.computeActionFromQValues(state, actions)

    def update(self, state, action, next_state, reward):
        nextactionvalues = self.computeValueFromQValues(nextState)

        actionvalue = self.getQValue(state,action)

        self.qvalues[(state, action)] = (1-self.alpha) * actionvalue + self.alpha * (reward + self.discount * nextactionvalues)


    def declare_action(self, valid_actions, hole_card, round_state):


        # # Estimate the win rate
        # win_rate = estimate_win_rate(100, self.num_players, hole_card, round_state['community_card'])
        #
        # action = getAction(hole_card, valid_actions)
        # # Check whether it is possible to call
        # can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        # if can_call:
        #     # If so, compute the amount that needs to be called
        #     call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        # else:
        #     call_amount = 0
        #
        # amount = None
        #
        # # If the win rate is large enough, then raise
        # if win_rate > 0.5:
        #     raise_amount_options = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']
        #     if win_rate > 0.85:
        #         # If it is extremely likely to win, then raise as much as possible
        #         action = 'raise'
        #         amount = raise_amount_options['max']
        #     elif win_rate > 0.75:
        #         # If it is likely to win, then raise by the minimum amount possible
        #         action = 'raise'
        #         amount = raise_amount_options['min']
        #     else:
        #         # If there is a chance to win, then call
        #         action = 'call'
        # else:
        #     action = 'call' if can_call and call_amount == 0 else 'fold'
        #
        # # Set the amount
        # if amount is None:
        #     items = [item for item in valid_actions if item['action'] == action]
        #     amount = items[0]['amount']

        return action, amount

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.wins += int(is_winner)
        self.losses += int(not is_winner)

def setup_ai():
    return QLearnBot()
