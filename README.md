# cs182-poker-player

Uses a handful of AI/ML techniques to train an agent to successfully (and even optimally) play variants of Poker.

Built using the amazing PyPokerEngine (https://github.com/ishikota/PyPokerEngine)

GUI (https://github.com/ishikota/PyPokerGUI)

## Dependencies
`pip install PyPokerEngine`

`pip install pypokergui`

## To Run
### Single game with GUI
First, run this command to automatically generate a config file (you can edit this later if you wish or re-run the command).

`python setupgame.py -a <ante> -b <blind_structure> -s <initial_stack> -r <max_round> -m <small_blind> -p <agentType>.py -n <numAgents>`

Sample command to setup default game, no args
`python setupgame.py`

Sample command to set game with some args
`python setupgame.py -a 5 -s 250 -r 5 -m 10 -p MonteCarloBot.py`


Now, run this command to start the server and play!

`pypokergui serve poker_conf.yaml --port 8000 --speed moderate`
### Command Line, Many Games (no GUI)
This command simulates many games running.

Example command line to run with default config
`python simulate.py -p MonteCarloBot -o FishBot -n 3 -g 10`

Example command line to run with custom config
`python simulate.py -p MonteCarloBot -o RandomBot -n 3 -g 10 -a 5 -s 500 -r 15 -m 15`

`simulate.py -p <agentType> -o <opponentType> -n <numOpponents> -g <numGames> -a <ante> -b <blind_structure> -s <initial_stack> -r <max_round> -m <small_blind> -t <numTraining> -w <writeToLog> -l <alpha> -e <epsilon> -d <discount> -v <rememberVals>`

Note that the latter three values `-l`, `-e`, and `-d` are only used in QLearning agents. If they are accidentally left in, the simulator will ignore them. The default values for these variables are not defined by `simulate.py`, but rather by the agents themselves in their `__init__` function.

If `-v` is included, the relevant values generated during training will be saved to the `saved_values` folder. These values will then be used by an agent run in the GUI, allowing you to play against the most recently trained agent of that type. This value is set to false by default, as it causes the agent to remember its most recent game - a significant issue if you're trying to run many trainings independently, but a fun way to see the results of your algorithms if you are not. To enable this feature, set `self.SAVEVALS` to `True` in `ZZZbot.py`.

This has to be done, even if you've used `-v` in your simulate command. This is an unfortunate side effect of the `PyPokerGUI`, which makes it difficult to propagate this command. In short: `-v` will save the values, change the value in `ZZZbot.py` to actually see the values reflected in the poker GUI.

It is also important that you use the same game configuration to run the GUI as you do to train the agent. Otherwise, the agent will have learned to play a completely different game, and will likely perform poorly even if it has a high win rate in simulation.

## Coding an Agent
Agents should be set up in their own python file. Ensure that the name of the agent is the same as the file (camelCase does not have to match), e.g. exampleagent.py contains ExampleAgent(). Although your agent can be named in camelcase, IT IS CRUCIAL THAT YOU DO NOT HAVE A FILE NAME IN CAMELCASE. File names should be in lowercase as one word - violating this invariant will break setupgame.py, which means you'll have to manually edit the poker_conf.yaml file.

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

would go after receive_round_result_message(), tabbed in at the same level as class FishPlayer().

### Examples
- MonteCarloBot: https://www.data-blogger.com/2017/11/01/pokerbot-create-your-poker-ai-bot-in-python/

### Documentation
- Official PyPokerEngine Documentation: https://ishikota.github.io/PyPokerEngine/
- More about callback functions: https://github.com/ishikota/PyPokerEngine/blob/master/AI_CALLBACK_FORMAT.md

# Report
<object data="https://github.com/Noah-Houghton/cs182-poker-player/blob/master/CS_182_Final_Project_Report.pdf" type="application/pdf" width="700px" height="700px">
    <embed src="https://github.com/Noah-Houghton/cs182-poker-player/blob/master/CS_182_Final_Project_Report.pdf">
        <p>This browser does not support PDFs. Please download the PDF to view it: <a href="https://github.com/Noah-Houghton/cs182-poker-player/blob/master/CS_182_Final_Project_Report.pdf">Download PDF</a>.</p>
    </embed>
</object>
