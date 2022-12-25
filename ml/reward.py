# reward.py - This module contains the code for defining the reward function for playing Tetris. It defines a Reward class that defines the reward function and provides methods for computing the reward for a given state.
 

class Reward:
    def __init__(self, beforeState, afterState, piece, action):
        # Compute the reward for the given state transition.
        self.beforeState = beforeState
        self.afterState = afterState
        self.piece = piece
        self.action = action
    
    def last_empty_row(self, board):
        # Initialize a variable to store the count of empty rows.
        count_empty_rows = 0

        # Iterate over the rows of the board, starting from the top.
        for i, row in enumerate(board):
            # If the row is empty (contains only zeros), increment the count of empty rows.
            if all(cell == 0 for cell in row):
                count_empty_rows += 1
            # If the row is not empty (contains any non-zero cells), exit the loop.
            else:
                break

        # Return the squared count of empty rows.
        return count_empty_rows ** 2

    def row_fill_fractions(self, board):
        # Define the sparsity values for the different number of occupied cells.
        sparsity_values = [0, 0.1111111111111111, 0.25, 0.42857142857142855, 0.6666666666666666, 1, 1.5, 2.3333333333333335, 4, 9, 100] # [0/10, 1/9, 2/8, 3/7, 4/6, 5/5, 6/4, 7/3, 8/2, 9/1, 100]

        # Initialize an empty list to store the fill fractions for each row.
        fill_fractions = []

        # Iterate over the rows of the board.
        for row in board:
            # Count the number of occupied cells in the row.
            occupied_cells = sum(cell == 1 for cell in row)

            # Calculate the fill fraction for the row.
            fill_fraction = sparsity_values[occupied_cells]

            # Add the fill fraction to the list.
            fill_fractions.append(fill_fraction)

            return fill_fractions

  
    def board_fill_fraction(self, board):
        # Count the number of occupied cells in the board.
        occupied_cells = sum(sum(row) for row in board)

        # Calculate the fill fraction.
        fill_fraction = occupied_cells / len(board) * len(board[0])

        return fill_fraction


    def pieceHasMoved(self):
        # Check if the piece has moved.
        yMove = self.piece["y"] - self.beforeState["piece"]["y"]
        if yMove > 0:
            return yMove
        else:
            return 0


    def distance_from_gap(self, state):
        assert(False) # unimplemented
        # Get the coordinates of the tetromino.
        tetromino_coords = get_tetromino_coords(state)

        # Get the coordinates of the gap in the line.
        gap_coords = get_gap_coords(state)

        # Calculate the distance between the tetromino and the gap.
        distance = calc_distance(tetromino_coords, gap_coords)

        return distance


    def get_reward(self):
        # Compute the reward for the given state transition.
        # Initialize a variable to store the reward.
        reward = 0
        reward += self.last_empty_row(self.afterState["board"]) - self.last_empty_row(self.beforeState["board"])
        reward += sum(self.row_fill_fractions(self.afterState["board"])) - sum(self.row_fill_fractions(self.beforeState["board"]))
        reward += self.board_fill_fraction(self.afterState["board"]) - self.board_fill_fraction(self.beforeState["board"])
        reward += self.pieceHasMoved()
        reward += self.afterState["score"] - self.beforeState["score"]
        reward += self.afterState["highScore"] - self.beforeState["highScore"]

        return reward


