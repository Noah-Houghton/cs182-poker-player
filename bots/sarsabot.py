from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card_from_deck
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import random as rand
import math
import util
from pypokerengine.api.emulator import Emulator

def estimateVictoryChance(nb_player, hole_card, community_card):
    # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
    # instead of binary win/lose, give the chance that we're gonna win
    community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
    unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
    opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
    opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
    my_score = HandEvaluator.eval_hand(hole_card, community_card)
    return my_score / max(opponents_score)

class SARSABot(BasePokerPlayer):
    def __init__(self):
        super(SARSABot, self).__init__()
        self.qvalues = util.Counter()
        self.epsilon = .2
        self.alpha = .5
        self.discount = .9
        self.roundWins = 0
        self.roundLosses = 0
        self.hand = None
        self.pot = 0
        self.cc = None
        self.prevAction = None
        self.prevState = None
        # self.latestReward = 0
        self.currAction = None
        self.currState = None
        self.currentInvestment = 0
        self.doUpdate = True

    def getQValue(self, state, action):
        if action not in ('fold', 'call', 'raise'):
            raise Exception("not an action")
        return self.qvalues[(state,action)]

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
        maxAction = None
        for action in actions:
            if self.getQValue(state, action["action"]) == max:
                # if util.flipCoin(.5):
                max = self.getQValue(state,action["action"])
                maxAction = action
            elif self.getQValue(state,action["action"]) > max:
                max = self.getQValue(state,action["action"])
                maxAction = action
        return maxAction

    def getAction(self, state, actions):
        if util.flipCoin(self.epsilon):
            return rand.choice(actions)
        else:
            return self.computeActionFromQValues(state, actions)

    def update(self, prev_state, prev_action, curr_state, curr_action, reward, round_state):
        if self.doUpdate:
            self.qvalues[(prev_state, prev_action["action"])] = self.getQValue(prev_state, prev_action["action"]) + self.alpha * (reward + (self.discount * self.getQValue(curr_state, curr_action["action"])) - self.getQValue(prev_state, prev_action["action"]))

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = gen_cards(round_state["community_card"])
        hole_card = gen_cards(hole_card)
        handStrength = HandEvaluator.eval_hand(hole_card, community_card)
        self.prevAction = self.currAction
        self.prevState = self.currState
        self.currState = handStrength
        choice = self.getAction(self.currState, valid_actions)
        action = choice["action"]
        amount = choice["amount"]
        if action == 'raise':
            # naively choose a random raise amt between min and max
            amt = rand.randint(amount["min"], amount["max"])
            choice["amount"] = amt
        self.currAction = choice
        if choice["amount"] > 0:
            self.currentInvestment += choice["amount"]
        # this happens only if the game ends after one action -- limiation of SARSA
        if not self.prevState == None and not self.prevAction == None:
            # change currState to change statespace
            # reward = self.getQValue(self.currState, self.currAction["action"])
            reward = 0
            self.update(self.prevState, self.prevAction, self.currState, self.currAction, reward, round_state)
        return choice["action"], choice["amount"]

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']
        self.ante = game_info["rule"]["ante"]
        self.max_round = game_info["rule"]["max_round"]
        self.small_blind_amount = game_info["rule"]["small_blind_amount"]

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hand = gen_cards(hole_card)
        self.roundStartMoney = [s["stack"] for s in seats if s["uuid"] == self.uuid][0]

    def receive_street_start_message(self, street, round_state):
        self.pot = round_state['pot']['main']['amount']
        self.cc = gen_cards(round_state['community_card'])

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.roundWins += int(is_winner)
        self.roundLosses += int(not is_winner)
        agentWon = [winner["stack"] for winner in winners if winner["uuid"] == self.uuid]
        reward = 0
        if is_winner:
            # get amount of money the agent gained by winning this round (?)
            reward = agentWon[0] - self.roundStartMoney
        else:
            if not self.prevState == None and not self.prevAction == None:
            # this occurs when the round ends after <1 action
                if self.currentInvestment == 0:
                    # small reward for not betting on a losing hand
                    reward = math.log(1)
                else:
                    # consider strength of hand so that we're not over-fitting
                    reward = -1 * (self.currentInvestment) + math.sqrt(self.currState)
                self.update(self.prevState, self.prevAction, self.currState, self.currAction, reward, round_state)
        # now that reward is dispensed, reset currentInvestment
        self.currentInvestment = 0
        # maybe need to reset vals here?
        self.cc = []
        self.pot = 0
        self.prevAction = None
        self.prevState = None
        self.currState = None
        self.currState = None
        self.currentInvestment = 0


def setup_ai():
    return SARSABot()
