# cs182-poker-player

Uses a handful of AI/ML techniques to train an agent to successfully (and even optimally) play variants of Poker.


## Dependencies
pip install PyPokerEngine
pip install pypokergui

## To Run
> pypokergui build_config --maxround 10 --stack 100 --small_blind 10 --ante 5 >> poker_conf.yaml

change ai_players in poker_conf.yaml to reflect the agent you want it to be

> pypokergui serve poker_conf.yaml --port 8000 --speed moderate

# TODO
- [ x ] terminal graphics
- [ x ] fix command line startup from fivecard-holdem.py
- [ x ] time from begin to end game
- [ ] parametrize bet / raise amount
- [ ] fix readme.md to describe project
- [ ] make different raise actions
- [ ] gather data!

## To Verify
- [ ] make sure that players have to ante
- [ ] no infinite games where n-1 players immediately fold

## Kyle
- [ ] Lookahead
- [ ] Etc.
## Phil
- [ ] Q-Learning
- [ ] HMM?
## Matt
- [ ] Advanced Agent
# Backlog
- [ ] implement allin if you can't make call
- [ ] implement check
- [ x ] small/large blind
- [ ] graphics
- [ ] keyboardAgent
- [ ] order of suits for highCard (?)
- [ ] abstract game rules for diff. kinds of poker
