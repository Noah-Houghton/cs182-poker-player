# cs182-poker-player

Uses a handful of AI/ML techniques to train an agent to successfully (and even optimally) play variants of Poker.

Built using the amazing PyPokerEngine (https://github.com/ishikota/PyPokerEngine)

GUI (https://github.com/ishikota/PyPokerGUI)

## Dependencies
pip install PyPokerEngine

pip install pypokergui

## To Run
### Command Line w/ GUI
setupgame.py -a <ante> -b <blind_structure> -s <initial_stack> -r <max_round> -sb <small_blind> -p <agentType>.py -n <numAgents>

pypokergui serve poker_conf.yaml --port 8000 --speed moderate

### Command Line, Many Games (no GUI)
simulate.py -a <agentType> -o <opponentType> -n <numOpponents> -g <numGames>

# Internal Checklist
## Kyle
- [ ] Lookahead
- [ ] Etc.
## Phil
- [ ] Q-Learning
- [ ] HMM?
## Matt
- [ ] Advanced Agent
