# initialize arbitrarily

# for each episode

    # init S
    # choose A from S using policy derived from Q
    # Repeat for each step
        # take action A, observe R, S'
        # choose A' from S' using policy derived from Q
        # Q(S,A) <- Q(S,A) + alpha[R + discountQ(S', A') - Q(S,A)]
        # S <- S'; A <- A';
    # until S is terminal
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card_from_deck
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import random as rand
import util
from pypokerengine.api.emulator import Emulator

def adjusted_montecarlo_simulation(nb_player, hole_card, community_card):
    # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
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
        self.epsilon = .1
        self.alpha = .3
        self.discount = 0
        self.wins = 0
        self.losses = 0
        self.hand = None
        self.pot = 0
        self.cc = None
        self.latestAction = None
        self.latestState = None

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

    def computeActionFromQValues(self, state, actions):
        if len(actions) == 0:
            return None
        max = float("-inf")
        maxAction = None
        for action in actions:
            if self.getQValue(state, action["action"]) == max:
                if util.flipCoin(.5):
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
        # prev_value = self.computeValueFromQValues(prev_state, [prev_action["action"]])
        # self.qvalues[(state, action["action"])] = self.qvalues[(state, action["action"])] + self.alpha * (reward + self.discount * self.qvalues[(next_state, nextAction["action"])] - self.qvalues[(state, action["action"])])
        self.qvalues[(prev_state, prev_action["action"])] = self.qvalues[(prev_state, prev_action["action"])] + self.alpha * (reward + self.discount * self.qvalues[(curr_state, curr_action["action"])] - self.qvalues[prev_state, prev_action["action"]])
        # print("updated state {} to value {}".format((prev_state, prev_action["action"]), self.getQValue(prev_state, prev_action["action"])))

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
            choice["amount"] = amount
        if not self.latestState == None and not self.latestAction == None:
            self.update(self.latestState, self.latestAction, (HandEvaluator.eval_hand(self.hand, self.cc), self.pot), choice,
                # (HandEvaluator.eval_hand(self.hand, gen_cards(round_state['community_card'])), round_state['pot']['main']['amount']),
                adjusted_montecarlo_simulation(self.num_players, self.hand, self.cc) * self.pot, round_state)
        self.latestAction = choice
        self.latestState = (HandEvaluator.eval_hand(self.hand, self.cc), self.pot)
        return action, amount

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']
        self.ante = game_info["rule"]["ante"]
        self.max_round = game_info["rule"]["max_round"]
        self.small_blind_amount = game_info["rule"]["small_blind_amount"]

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hand = gen_cards(hole_card)
        self.cc = []
        self.pot = 0

    def receive_street_start_message(self, street, round_state):
        # if street != 'preflop':

        self.pot = round_state['pot']['main']['amount']
        self.cc = gen_cards(round_state['community_card'])

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.wins += int(is_winner)
        self.losses += int(not is_winner)

def setup_ai():
    return SARSABot()
