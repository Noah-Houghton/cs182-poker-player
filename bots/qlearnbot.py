from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
from pypokerengine.utils.game_state_utils import _restore_table
import time
import random as rand
import util
import math


class QLearnBot(BasePokerPlayer):
    def __init__(self):
        super(QLearnBot, self).__init__()
        self.qvalues = util.Counter()
        self.epsilon = .15
        self.alpha = .3
        self.discount = 1
        self.roundWins = 0
        self.roundLosses = 0
        self.hand = None
        self.pot = 0
        self.curCC = None
        self.latestAction = None
        self.seats = []
        self.latestBet = 0
        self.lastState = None
        self.haveActed = False
        self.currentMoney = 0
        self.currentInvestment = 0

    def getState(self, strength):
        return int(math.log(strength, 1.05))
        # return strength 

    def getLegalActions(self, round_state):
        table = _restore_table(round_state)
        players = table.seats.players
        return ActionChecker.legal_actions(players, 0, round_state["small_blind_amount"])

    def getQValue(self, state, action):
        return self.qvalues[(state,action)]

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
        maxAction = None
        for action in actions:
            qval = self.getQValue(state, action["action"])
            if qval == max:
                if util.flipCoin(.5):
                    max = qval
                    maxAction = action
            elif qval > max:
                max = qval
                maxAction = action
        return maxAction

    def getAction(self, state, actions):
        if actions == []:
            print None
        if util.flipCoin(self.epsilon):
            return rand.choice(actions)
        else:
            return self.computeActionFromQValues(state, actions)

    def update(self, state, action, next_state, reward, new_round_state):
        nextactionvalue = 0
        if next_state != None:
            nextactionvalue = self.computeValueFromQValues(next_state, self.getLegalActions(new_round_state))
        actionvalue = self.getQValue(state,action)
        self.qvalues[(state, action)] = ((1-self.alpha) * actionvalue) + (self.alpha * (reward + (self.discount * nextactionvalue)))


    def declare_action(self, valid_actions, hole_card, round_state):
        newCC = gen_cards(round_state['community_card'])
        cur_state = self.getState(HandEvaluator.eval_hand(self.hand, self.curCC))
        new_state = self.getState(HandEvaluator.eval_hand(self.hand, newCC))
        if self.haveActed:
            self.update(cur_state, self.latestAction, new_state, 0, round_state)
        self.curCC = newCC
        choice = self.getAction(new_state, valid_actions)
        action = choice["action"]
        amount = choice["amount"]
        if action == 'raise':
            # naively choose a random raise amt between min and max
            amount = rand.randrange(amount["min"], max(amount["min"], amount["max"]) + 1)
        self.latestAction = action
        self.latestBet = amount
        self.currentInvestment += self.latestBet
        self.haveActed = True
        self.played_in_round = True
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
        agentWon = [winner["stack"] for winner in winners if winner["uuid"] == self.uuid]
        reward = 0
        if is_winner:
            reward = (agentWon[0] - self.currentMoney)
            reward = math.log(reward) 
        elif self.currentInvestment > 0:
            reward = math.log(self.currentInvestment) * -1.0
        cur_state = self.getState(HandEvaluator.eval_hand(self.hand, self.curCC))
        if self.haveActed:
            self.update(cur_state, self.latestAction, None, reward, round_state)

def setup_ai():
    return QLearnBot()
