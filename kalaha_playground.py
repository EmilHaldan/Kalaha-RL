import numpy as np
import random as rn
import pandas as pd
import time 



class Cavity:
    # Create a class boiler plate for the cavity
    def __init__(self, player, index, stones=6):
        self.stones = stones
        self.next = None  # Pointer to the next cavity
        self.player = player
        self.index = index

    def __str__(self):
        return f"{self.stones}"

    def __repr__(self):
        return "cavity"

    def pickup(self):
        # Use the stones in the cavity
        stones = self.stones
        self.stones = 0
        return stones

    def add(self, stones):
        # Add stones to the cavity
        self.stones += stones
        return self.stones


class Goal (Cavity):
    # Make goal a subclass of cavity
    def __init__(self, player):
        self.stones = 0
        self.next = None
        self.player = player
        self.index = "goal"

    def __str__(self):
        return f"{self.stones}"

    def __repr__(self):
        return "goal"

    def pickup(self):
        # Undefine pickup as its not possible.
        return False


class Board:
    # Create a class boiler plate for the board
    def __init__(self, verbose=False):
        self.player1 = [Cavity(player=1, index=i) for i in range(6)] 
        self.player1_goal = Goal(player=1)
        self.player1[0].stones = 7 # adjustment to avoid starting advantage
        self.player2 = [Cavity(player=2, index=i) for i in range(6)] 
        self.player2_goal = Goal(player=2)
        self.player2[0].stones = 7 # adjustment to avoid starting advantage
        self.turn_number = 0
        self.verbose = verbose

         # Link the cavities and goals to form a circular board
        for i in range(5):
            self.player1[i].next = self.player1[i + 1]
            # print("Player 1 hole ", i, " points to ", i + 1)
        self.player1[5].next = self.player1_goal
        # print("Player 1 hole 0 points to player 1 goal")

        for i in range(5):
            self.player2[i].next = self.player2[i + 1]
            # print("Player 2 hole ", i, " points to ", i + 1)
        self.player2[5].next = self.player2_goal
        # print("Player 2 hole 5 points to player 2 goal")

        # Link goals and sides
        self.player1_goal.next = self.player2[0]
        self.player2_goal.next = self.player1[0]
        # print("Player 1 goal points to player 2 hole 0")
        # print("Player 2 goal points to player 1 hole 0")

    def __str__(self):

        # print(type(self.player1[0]))
        # print(self.player1[0])
        print("")
        print(f"   0:({str(self.player2[0]):2})    1:({str(self.player2[1]):2})    2:({str(self.player2[2]):2})    3:({str(self.player2[3]):2})    4:({str(self.player2[4]):2})    5:({str(self.player2[5]):2})")
        print(f"  (   {str(self.player1_goal):4} ) <--- Player 1           Player2 ---> (   {str(self.player2_goal):4} )       ROUND: {self.turn_number}")
        print(f"   5:({str(self.player1[5]):2})    4:({str(self.player1[4]):2})    3:({str(self.player1[3]):2})    2:({str(self.player1[2]):2})    1:({str(self.player1[1]):2})    0:({str(self.player1[0]):2})")
        return ""


    def check_if_cavity_empty(self, player, cavity_index , verbose=False):
        """
        Check if the selected cavity is empty.
        """
        if player not in [1, 2]:
            print("Player must be int: 1 or 2")
            return False

        if player == 1:
            player_side = self.player1
        elif player == 2:
            player_side = self.player2

        if player_side[cavity_index].stones == 0:
            return True
        else:
            return False

    def check_if_side_empty(self, player, verbose=False):
        """
        Check if the selected side is empty.
        """
        if player not in [1, 2]:
            print("Player must be int: 1 or 2")
            return False

        if player == 1:
            player_side = self.player1
        elif player == 2:
            player_side = self.player2

        for i in range(6):
            if player_side[i].stones != 0:
                return False
        
        # Place all opponent's stones in the player's goal
        if verbose:
            print(f"Player {player} has no stones left on the side. The player gets the remaining stones on the opponent's side.")
        
        if player == 1:
            for i in range(6):
                self.player1_goal.add(self.player2[i].pickup())
        else:
            for i in range(6):
                self.player2_goal.add(self.player1[i].pickup())

        # Print final score and end game
        if verbose:
            print("\n"*2)
            print("GAME OVER!  -  Final score:")
            print(self)
        return True
        


    def take_turn(self, player, cavity_index, verbose=False):
        """
        Take a turn for the current player, starting from the selected cavity.

        Return True if the player gets another turn.
        Return False if the turn is over.
        """
        if player not in [1, 2]:
            if verbose:
                print("Player must be int: 1 or 2")
            return False
        
        if player == 1:
            player_side = self.player1
        elif player == 2:
            player_side = self.player2

        
        current_cavity = player_side[cavity_index]
        on_cur_player_side = True
        stones = current_cavity.pickup()

        if stones == 0:
            if verbose:
                print(f"Selected cavity ({cavity_index}) is empty")
            return True 

        # Distribute stones
        while stones > 0:
            current_cavity = current_cavity.next
            if verbose:
                print(f"SIDE: player{player if on_cur_player_side else player%2 + 1}   INDEX: {current_cavity.index}   CUR STONE: {stones}")
            
            if repr(current_cavity) == "goal":
                on_cur_player_side = False
                if current_cavity.player != player:
                    on_cur_player_side = True
                    continue  # Skip opponent's goal

            current_cavity.add(1)
            stones -= 1

            if verbose:
                time.sleep(1)
                if current_cavity.index == "goal":
                    print(f"Ball Drop:  Player {player} GOT 1 POINT!")
                elif on_cur_player_side:
                    print(f"Ball Drop:  Player {player} added a stone to own side cavity-{current_cavity.index}")
                else:
                    print(f"Ball Drop:  Player {player} added a stone to opposite side cavity-{current_cavity.index}")
                print(self)

            if stones == 0:
                if current_cavity.player != player:
                    # skip if ending in opponent's side
                    if verbose:
                        print(f"Turn Over - Player {player} ended in opponent's side - Turn Over")
                        print(self)
                    return False
                else: # Is current players side
                    # Check if ending in own goal
                    if repr(current_cavity) == "goal":
                        if verbose:
                            print(f"Player {player} ended in own goal. Take another turn")
                            print(self)
                        return True
                    elif current_cavity.stones > 1 and current_cavity.player == player:
                        # Take the stones from the current cavity and keep playing
                        if verbose:
                            print(f"Player {player} ended in own non-empty cavity number {current_cavity.index}. Continue from here")
                            print(self)
                        stones = current_cavity.pickup()
                        continue
                    elif current_cavity.stones == 1:
                        # Add stones from opposite cavity to own goal if ending in own empty cavity and end turn
                        opposite_cavity_index = 5 - current_cavity.index
                        if player == 1:
                            self.player1_goal.add(self.player1[current_cavity.index].pickup())
                            self.player1_goal.add(self.player2[opposite_cavity_index].pickup())
                        else:
                            self.player2_goal.add(self.player2[current_cavity.index].pickup())
                            self.player2_goal.add(self.player1[opposite_cavity_index].pickup())
                        if verbose:
                            print(f"Turn Over - Player {player} ended up in own empty cavity, takes stones from opposite cavity, and ends turn - Turn Over")
                            print(self)
                        return False
        return False


def play_random_game(verbose=True):
    game = Board()
    if verbose:
        print(game)


    while True:
        game.turn_number += 1
        for player in [1, 2]:
            if verbose:
                print("\n"*3)
                print(f"Turn: {game.turn_number}   Player {player}")

            try:
                player_take_turn = True
                while player_take_turn:

                    if game.check_if_side_empty(player, verbose):
                        return True

                    cavity_index = rn.randint(0, 5)
                    if game.check_if_cavity_empty(player, cavity_index, verbose):
                        continue

                    if verbose:
                        print("Board before turn: ")
                        print(game)
                        print("")
                        if player == 1:
                            print(f"Player {player} selected cavity {cavity_index} and picks up {game.player1[cavity_index].stones} stones")
                        else:
                            print(f"Player {player} selected cavity {cavity_index} and picks up {game.player2[cavity_index].stones} stones")
                    player_take_turn = game.take_turn(player, cavity_index, verbose)
                    
                    if game.check_if_side_empty(player, verbose):
                        return True
                
                    
                tmp = input("Press Enter to continue...")
            except ValueError:
                print("Invalid input. Please enter a number between 0 and 5.")


if __name__ == "__main__":
    play_random_game(verbose=True)