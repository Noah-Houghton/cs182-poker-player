from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
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

class QLearnBot(BasePokerPlayer):
    def __init__(self):
        super(QLearnBot, self).__init__()
        self.qvalues = util.Counter()
        self.epsilon = .1
        self.alpha = .5
        self.discount = 1
        self.roundWins = 0
        self.roundLosses = 0
        self.hand = None
        self.pot = 0
        self.cc = None
        self.latestAction = None
        self.seats = []
        self.latestBet = 0

    def getLegalActions(self, round_state):
        street = round_state["street"]
        min_raise = 0
        if street in round_state["action_histories"].keys():
            moves = round_state["action_histories"][street]
            for move in moves:
                if move["amount"] > min_raise:
                    min_raise = move["amount"]
        min_raise = max(round_state["small_blind_amount"], min_raise) # min raise - last bet
        max_raise = self.seats[0]["stack"]
        if max_raise < min_raise:
            min_raise = max_raise = -1
        return [
            { "action" : "fold" , "amount" : 0 },
            { "action" : "call" , "amount" : (min_raise - self.latestBet)},
            { "action" : "raise", "amount" : { "min": (min_raise + 1), "max": max_raise } }
        ]

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
        if util.flipCoin(self.epsilon):
            return rand.choice(actions)
        else:
            return self.computeActionFromQValues(state, actions)

    def update(self, state, action, next_state, reward, round_state):
        nextactionvalues = 0
        if next_state != None:
            nextactionvalues = self.computeValueFromQValues(next_state, self.getLegalActions(round_state))
        actionvalue = self.getQValue(state,action)
        self.qvalues[(state, action)] = (1-self.alpha) * actionvalue + self.alpha * (reward + self.discount * nextactionvalues)


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
            self.update((HandEvaluator.eval_hand(self.hand, self.cc)), self.latestAction,
                (HandEvaluator.eval_hand(self.hand, gen_cards(round_state['community_card'])), round_state['pot']['main']['amount']),
                0, round_state)
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
        if len(agentWon) != 0:
            reward = agentWon[0]
        self.update((HandEvaluator.eval_hand(self.hand, self.cc)), self.latestAction, None, reward, round_state)


def setup_ai():
    return QLearnBot()
