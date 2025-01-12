This repo is a simple late night procrastination project, which started with "what if?". The model training and the playground are far from optimal, leaving plenty of space for increasing effeciency and model performance. 


kalaha_playground.py facilitates the Board class which is the centerpiece of the game. 

RL_Bot.py converts the Board class into a gym environment which is used by some high level RL lib. The parameter is set to use an MLP, and has some predifined best-estimate values for epsilon.
All parameters are almost certainly sub optimal. Pull-requests for better model configurations are welcome.

Man_vs_Machine.py loads a trained model, and lets a human play against the first and only trained model.

The model is not very good and often makes moves which are suboptimal. This is most likely due to the reward function only considering points gained per turn.
