# from documentation at https://github.com/ishikota/PyPokerEngine
from pypokerengine.players import BasePokerPlayer

class FishBot(BasePokerPlayer):


    def __init__():
        super(FishBot, self).__init__()
        self.roundWins = 0
        self.roundLosses = 0

    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.roundWins += int(is_winner)
        self.roundlosses += int(not is_winner)

def setup_ai():
    return FishBot()
