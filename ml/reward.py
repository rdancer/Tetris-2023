# reward.py - This module contains the code for defining the reward function for playing Tetris. It defines a Reward class that defines the reward function and provides methods for computing the reward for a given state.
 

class Reward:
    def __init__(self, beforeState, board_after):
        # Compute the reward for the given state transition.
        self.beforeState = beforeState
        self.board_after = board_after
        # print("Reward: board_after: ", board_after)
        self.num_completed_rows, self.board_after_cleared = self.clear_rows(board_after)
        self.score_after = self.beforeState["score"] + self.num_completed_rows
        self.high_score_after = max(self.beforeState["highScore"], (self.score_after - self.beforeState["score"]))
        # return self # TypeError: __init__() should return None, not 'Reward'
    
    def clear_rows(self, board):
        """Clear any rows that are full and return the number of cleared rows."""
        if board is None:
            return 0, None

        # Initialize a variable to store the number of cleared rows.
        num_cleared_rows = 0

        # Iterate over the rows of the board, starting from the top.
        for i in range(len(board)):
            row = board[i]
            # If the row is full (contains only non-zero cells), clear the row.
            if all(cell != 0 for cell in row):
                # Clear the row.
                board[i] = [0] * len(row)

                # Increment the number of cleared rows.
                num_cleared_rows += 1

        # If any rows were cleared, shift the remaining rows down.
        if num_cleared_rows > 0:
            # Shift the remaining rows down.
            board = self._shift_rows_down(board, num_cleared_rows)

        # Return the number of cleared rows and the new board.
        return num_cleared_rows, board


    def _shift_rows_down(self, board, num_rows):
        """Prepend the given number of empty rows to the board."""
        new_board = []
        for i in range(num_rows):
            new_board.append([0] * len(board[0]))
        for row in board:
            new_board.append(row)
        return new_board


    def last_empty_row(self, board):
        """Return the index of the last empty row in the board."""
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
        """Return a list of the fill fractions for each row in the board. It really returns fill *ratio*, i.e. the ratio of filled cells not to total cells, but to *unfilled* cells, which makes it grow non-linearly. We do this because holes are a pain in the neck, and we want to incentivise filling them."""
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
        """Return the fill fraction of the board, i.e. how many filled cells vs how many empty cells the board has."""
        # Count the number of occupied cells in the board.
        occupied_cells = sum(sum(row) for row in board)

        # Calculate the fill fraction.
        fill_fraction = occupied_cells / len(board) * len(board[0])

        return fill_fraction


    def get_reward(self):

        # XXX these are invalid boards, or most likely invalid
        if self.board_after is None:
             return -42000 # Do not do this move at all
        # if board is full of zeroes (this would only happen at the beginning, in which case just put a piece down)
        if self.board_after == [[0 for i in range(10)] for j in range(20)]:
            return -42000 # Do not do this move at all


        # Compute the reward for the given state transition.

        keep_height_low = (self.last_empty_row(self.board_after_cleared) - self.last_empty_row(self.beforeState["board"])) * 10
        fill_rows_evenly = sum(self.row_fill_fractions(self.board_after_cleared)) - sum(self.row_fill_fractions(self.beforeState["board"]))
        keep_board_empty = self.board_fill_fraction(self.board_after_cleared) - self.board_fill_fraction(self.beforeState["board"])
        increase_score = self.score_after - self.beforeState["score"]
        careful_when_score_high = self.high_score_after - self.beforeState["highScore"]
        complete_rows = self.num_completed_rows ** 1.5 * 100 # really juicy, and gets more juicier the more row we clear at a time

        total_reward = keep_height_low + fill_rows_evenly + keep_board_empty + increase_score + careful_when_score_high + complete_rows
        
        print( 'reward: ', total_reward, ': keep_height_low: ', keep_height_low, 'fill_rows_evenly: ', fill_rows_evenly, 'keep_board_empty: ', keep_board_empty, 'increase_score: ', increase_score, 'careful_when_score_high: ', careful_when_score_high, 'complete_rows: ', complete_rows)

        return total_reward


