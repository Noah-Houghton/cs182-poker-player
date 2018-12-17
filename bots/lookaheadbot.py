# from https://www.data-blogger.com/2017/11/01/pokerbot-create-your-poker-ai-bot-in-python/
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import numpy as np
import time
import random as rand
import util

def hand_strength(nb_simulation, nb_player, hole_card, community_card=None):
    if not community_card: community_card = []

    # Make lists of Card objects out of the list of cards
    community_card = gen_cards(community_card)
    hole_card = gen_cards(hole_card)

    # Estimate the utility of the current hand by "looking ahead"
    utility = sum([lookaheadfeature(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
    return utility


def lookaheadfeature(nb_player, hole_card, community_card):
    # Function to "look ahead" to future cards
    community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
    unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
    my_score = HandEvaluator.eval_hand(hole_card, community_card)
    return my_score

class LookAheadBot(BasePokerPlayer):
    def __init__(self):
        self.wins = 0
        self.losses = 0
        self.roundWins = 0
        self.roundLosses = 0
        self.hand = None
        self.pot = 0
        self.cc = None
        self.latestAction = None
        self.seats = []
        self.latestBet = 0

    def declare_action(self, valid_actions, hole_card, round_state):

        hand_utility = hand_strength(100, self.num_players, hole_card, round_state['community_card'])

        # See if can call
        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        if can_call:
            # If so, compute the amount that needs to be called
            call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        else:
            call_amount = 0

        amount = None

        if hand_utility > 20000000:
            raise_amount_options = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']
            if hand_utility > 40000000:
                # If utility is high, raise as much as possible
                action = 'raise'
                amount = raise_amount_options['max']
            elif hand_utility > 25000000:
                # If it is only somewhat likeley to win, then raise by the minimum amount possible
                action = 'raise'
                amount = raise_amount_options['min']
            else:
                # If there is a chance to win, then call
                action = 'call'
        else:
            action = 'call' if can_call and call_amount == 0 else 'fold'

        # Set the amount
        if amount is None:
            items = [item for item in valid_actions if item['action'] == action]
            amount = items[0]['amount']
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
        self.roundWins += int(is_winner)
        self.roundLosses += int(not is_winner)
        agentWon = [winner["stack"] for winner in winners if winner["uuid"] == self.uuid]


def setup_ai():
    return LookAheadBot()
