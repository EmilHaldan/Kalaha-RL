import numpy as np
import random as rn
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import BaseCallback

from gym import Env
from gym.spaces import Discrete, Box

from kalaha_playground import Board
from datetime import datetime
import time


class KalahaEnv(Env):
    def __init__(self, verbose = False, model=None):
        super(KalahaEnv, self).__init__()
        self.verbose = verbose
        self.board = Board(verbose=self.verbose)
        self.action_space = Discrete(6)
        self.observation_space = Box(low=0, high=48, shape=(14,), dtype=np.int32)
        self.previous_score = 0
        self.model = model  # Reference to the RL agent
        self.reset()

    def reset(self):
        self.board = Board(verbose=self.verbose)
        self.turn_count = 0  # Track the number of turns in the episode
        self.episode_reward = 0  # Accumulate rewards for the episode
        self.previous_score = 0
        return self.get_state()

    def step(self, action):
        player = 2  # Assuming the RL agent always plays as Player 2
        opponent = 1 # Assuming the opponent is Player 1

        if self.board.check_if_cavity_empty(player, action):
            reward = -1  # Penalize invalid actions
            done = False
            info = {
                "episode_score": self.board.player2_goal.stones,
                "episode_turns": self.turn_count,
                "episode_reward": self.episode_reward,
            }
            return self.get_state(), reward, done, info

        # Check if the game is over
        done = self.board.check_if_side_empty(1) or self.board.check_if_side_empty(2)

        # Take the action
        agent_turn = True
        while agent_turn:
            if done:
                break
            done = self.board.check_if_side_empty(1) or self.board.check_if_side_empty(2)
            if done:
                break
            # Execute the action
            agent_turn = self.board.take_turn(player, action, verbose=self.verbose)

            # Compute reward after the move
            reward = self.board.player2_goal.stones - self.previous_score
            self.previous_score = self.board.player2_goal.stones
            self.episode_reward += reward

            # If the agent gets another turn, use the model to predict the next action
            if agent_turn:
                if self.model is not None:
                    action, _states = self.model.predict(self.get_state(), deterministic=True)
                    # If it's picking an invalid action, penalize it, and remove its bonus turn
                    if self.board.check_if_cavity_empty(player, action):
                        reward = -1
                        break

        self.turn_count += 1  # Increment turn count


        # Check if the game is over
        done = self.board.check_if_side_empty(1) or self.board.check_if_side_empty(2)

        # Handling opponent's turn (Player 1's turn - Random agent)
        if not done:
            opponent_turn = True
            while opponent_turn:
                done = self.board.check_if_side_empty(1) or self.board.check_if_side_empty(2)
                if done:
                    break
                opponent_choice = rn.randint(0, 5)
                opp_cavity_empty = self.board.check_if_cavity_empty(opponent, opponent_choice)
                if not opp_cavity_empty:
                    opponent_turn = self.board.take_turn(opponent, opponent_choice, verbose=self.verbose)

        # Check if the game is over
        done = self.board.check_if_side_empty(1) or self.board.check_if_side_empty(2)

        self.board.turn_number += 1
        # Provide info for metrics tracking
        info = {
            "episode_score": self.episode_reward,
            "episode_turns": self.turn_count,
            "episode_reward": self.episode_reward
        }

        return self.get_state(), reward, done, info

    def get_state(self):
        # Flatten the board state into a vector
        return np.array(
            [c.stones for c in self.board.player1] +
            [self.board.player1_goal.stones] +
            [c.stones for c in self.board.player2] +
            [self.board.player2_goal.stones]
        )


class KalahaMetricsCallback(BaseCallback):
    def __init__(self, log_interval=100, verbose=0):
        super(KalahaMetricsCallback, self).__init__(verbose)
        self.total_score = 0
        self.total_turns = 0
        self.avg_turns_to_win = 0
        self.total_reward = 0
        self.episode_count = 0
        self.log_interval = log_interval
        self.episode_rewards = []
        self.start_time = time.time()
        self.interval_time = time.time()

    def _on_step(self) -> bool:
        # Collect environment info at the end of each episode
        if self.locals["dones"][0]:  # Check if the episode is done
            info = self.locals["infos"][0]
            episode_score = info.get("episode_score", 0)  # Assuming 'episode_score' is tracked
            episode_turns = info.get("episode_turns", 0)  # Assuming 'episode_turns' is tracked
            episode_reward = info.get("episode_reward", 0)  # Sum of rewards for this episode
            
            # Accumulate totals for averages
            self.total_score += episode_score
            self.total_turns += episode_turns
            self.total_reward += episode_reward
            self.episode_count += 1

            if self.verbose > 0:
                if self.episode_count % self.log_interval == 0:
                    avg_reward = self.total_reward / self.log_interval
                    avg_turns = self.total_turns / self.log_interval

                    # Get model loss and exploration rate (epsilon)
                    epsilon = self.model.exploration_rate if hasattr(self.model, 'exploration_rate') else None
                    loss    = self.model.loss if hasattr(self.model, 'loss') else None

                    print("Datetime: ", datetime.now())
                    print(f"Time Elapsed (s): ", int(time.time() - self.start_time))
                    print(f"Interval Time Elapsed (s): ", int(time.time() - self.interval_time))
                    print(f"Episode {self.episode_count} - Last {self.log_interval} Avg Reward: {avg_reward:.2f}")
                    print(f"Avg Turns: {avg_turns:.2f}")
                    if loss is not None:
                        print(f"Model Loss: {loss:.4f}")
                    if epsilon is not None:
                        print(f"Epsilon: {epsilon:.4f}")
                    print("")

                    # Reset totals
                    self.total_score = 0
                    self.total_turns = 0
                    self.total_reward = 0
                    self.interval_time = time.time()

        return True



if __name__ == "__main__":

    env = KalahaEnv(verbose=False)
    total_timesteps = 100000000
    model = DQN("MlpPolicy", env = env, 
                exploration_fraction= 0.7,
                exploration_initial_eps= 0.99, # Initial epsilon value (1 = random actions, 0 = no random actions)
                exploration_final_eps= 0.05, # Final epsilon value (after exploration_fraction * total_timesteps)
                learning_starts= int(total_timesteps*0.1), # Number of steps before learning starts
                learning_rate=0.00001,
                verbose=0)

    # Training the RL bot
    # Attach the model to the environment
    env.model = model
    callback = KalahaMetricsCallback(log_interval=1000, verbose=1)
    model.learn(total_timesteps=total_timesteps, callback=callback, progress_bar=True)

    # Save the model
    model.save("models/kalaha_model_2")
    print("Model saved!")

    # Load the model
    # model = DQN.load("kalaha_model")
