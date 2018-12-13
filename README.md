# cs182-poker-player

Uses a handful of AI/ML techniques to train an agent to successfully (and even optimally) play variants of Poker.

Built using the amazing PyPokerEngine (https://github.com/ishikota/PyPokerEngine)

GUI (https://github.com/ishikota/PyPokerGUI)

## Dependencies
`pip install PyPokerEngine`

`pip install pypokergui`

## To Run
### Command Line w/ GUI

`setupgame.py -a <ante> -b <blind_structure> -s <initial_stack> -r <max_round> -sb <small_blind> -p <agentType> -n <numAgents>`

`pypokergui serve poker_conf.yaml --port 8000 --speed moderate`
### Command Line, Many Games (no GUI)
`simulate.py -a <agentType> -o <opponentType> -n <numOpponents> -g <numGames>`


## Coding an Agent
Agents should be set up in their own python file. Ensure that the name of the agent is the same as the file (camelCase does not have to match), e.g. exampleagent.py contains ExampleAgent().

Agents have to implement the following functions:
~~~~
class FishPlayer(BasePokerPlayer):  # Do not forget to make parent class "BasePokerPlayer"
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
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
        pass
~~~~

Each file should have a function defined at the bottom of the file outside the class code which implements setup_ai(), which returns an object of the class type. For example:

`setup_ai(): return exampleAgent()`

### Examples
- MonteCarloBot: https://www.data-blogger.com/2017/11/01/pokerbot-create-your-poker-ai-bot-in-python/

### Documentation
- Official PyPokerEngine Documentation: https://ishikota.github.io/PyPokerEngine/
- More about callback functions: https://github.com/ishikota/PyPokerEngine/blob/master/AI_CALLBACK_FORMAT.md
    - Goes through what each function is actually receiving, will be useful when building our agents.

### Algorithms
- SARSA (https://en.wikipedia.org/wiki/State%E2%80%93action%E2%80%93reward%E2%80%93state%E2%80%93action)

# Internal Checklist
## Kyle
- [ ] Lookahead
- [ ] Etc.
## Phil
- [ ] Q-Learning
- [ ] HMM?
## Matt
- [ ] Advanced Agent
