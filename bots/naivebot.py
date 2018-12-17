from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import gen_cards
import math

class NaiveBot(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        # checks strength of hand
        community_card = gen_cards(round_state["community_card"])
        hole_card = gen_cards(hole_card)
        handStrength = HandEvaluator.eval_hand(hole_card, community_card)
        strength = math.log(handStrength)
        if strength < 6:
            return valid_actions[0]['action'], valid_actions[0]['amount']
        elif strength >= 6 and strength < 13:
            return valid_actions[1]['action'], valid_actions[1]['amount']
        elif strength >= 13 and strength < 17:
            return valid_actions[2]['action'], valid_actions[2]['amount']['min']
        elif strength >= 17:
            return valid_actions[2]['action'], valid_actions[2]['amount']['max']
        else:
            raise Exception("no action selected")

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
    return NaiveBot()
