import numpy as np
import random as rn
from kalaha_playground import Board
from stable_baselines3 import DQN
from datetime import datetime
import time


def play_human_vs_machine(model_path):
    # Load the pre-trained model
    model = DQN.load(model_path)

    # Initialize the game board
    game = Board(verbose=True)

    print("Welcome to Kalaha! Player 1 is Human, Player 2 is the AI.")
    print(game)

    while True:
        game.turn_number += 1
        
        # Human Turn
        print("\n"*3)
        print("\nPlayer 1's Turn")
        human_turn = True
        while human_turn:
            try:
                # Get human input
                cavity_index = int(input("Choose a cavity (0-5): "))
                if cavity_index < 0 or cavity_index > 5:
                    print("Invalid input. Please choose a number between 0 and 5.")
                    continue

                if game.check_if_cavity_empty(1, cavity_index):
                    print("Cavity is empty. Choose a different cavity.")
                    continue

                # Take the turn
                human_turn = game.take_turn(1, cavity_index, verbose=True)

                if game.check_if_side_empty(1, verbose=True):
                    return

            except ValueError:
                print("Invalid input. Please enter a number between 0 and 5.")

        print(game)

        # AI Turn
        print("\n"*3)
        print("\nPlayer 2's Turn (AI)")
        ai_turn = True
        while ai_turn:
            # Get the AI's action
            state = np.array([
                [c.stones for c in game.player1] +
                [game.player1_goal.stones] +
                [c.stones for c in game.player2] +
                [game.player2_goal.stones]
            ])

            action, _states = model.predict(state, deterministic=True)
            action = action[0]
            print("###   AI action:   ", action, "    ###")   
            print("\n")
            print(game)
            print("\n"*2)
            input("Press Enter to continue...")
            

            if game.check_if_cavity_empty(2, action):
                print(f"AI chose an empty cavity ({action}). Skipping its turn.")
                break

            ai_turn = game.take_turn(2, action, verbose=True)

            if game.check_if_side_empty(2, verbose=True):
                print("Game Over! Player 2 (AI) wins!")
                return

        print(game)

if __name__ == "__main__":
    model_path = "models/kalaha_model"
    play_human_vs_machine(model_path)

