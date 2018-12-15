# from https://www.data-blogger.com/2017/11/01/pokerbot-create-your-poker-ai-bot-in-python/
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import numpy as np
import time
import random as rand
import util

class LookAheadBot(BasePokerPlayer):
    def __init__(self):

    def lookahead(self, state, action):
        #TODO
        """
        Get a list of possible cards left
        Let max_possible_score = 0
        For each card in cards left
            score = (likelihood of that card appearing)*HandEvaluator.eval_hand(future hand)
            score_sum += score
        if score_sum > 2*(HandEvaluator.eval_hand(future hand))
            Raide
        if score_sum > 1.5*(HandEvaluator.eval_hand(future hand))
            Call
        if score_sum > 1.25(HandEvaluator.eval_hand(future hand))
            Fold

        Put each one of those in your hand
        """

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return LookAheadBot()
