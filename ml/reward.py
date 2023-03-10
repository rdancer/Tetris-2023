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
        self.reward_tally = 0
    
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


    def empty_rows(self, board):
        return len([row for row in board if all(cell == 0 for cell in row)])

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

    def sum_row_fill_fractions(self, board):
        """Return the sum of the fill fractions for the rows in the board."""
        return sum(self.row_fill_fractions(board))

    def dead_space(self, board):
        """Return the number of empty but inaccessible cells in the board."""
        dead_cell_count = 0
        covered_columns = [False] * len(board[0])
        for row in board:
            for i, cell in enumerate(row):
                if cell == 1:
                    covered_columns[i] = True
                else:
                    if covered_columns[i]:
                        dead_cell_count += 1
        return dead_cell_count

    def bumpiness(self, board):
        """Return the sum of the absolute differences between adjacent columns."""
        bumpiness = 0
        for i in range(len(board[0]) - 1):
            bumpiness += abs(self.column_height(board, i) - self.column_height(board, i + 1))
        return bumpiness

    def column_height(self, board, column):
        """Return the height of the given column."""
        for i, row in enumerate(board):
            if row[column] == 1:
                return len(board) - i
        return 0

    def print_boards(self, board1, board2):
        """Print the two boards side-by-side."""
        for i in range(len(board1)):
            print(board1[i], board2[i])
        print()

    def punish_increase(self, func, coefficient=1, **kwargs):
        """Punish an increase in the value of the given function."""
        self.reward_increase(func, -coefficient, **kwargs)

    def reward_increase(self, func, coefficient=1, **kwargs):
        """Reward an increase in the value of the given function."""
        if kwargs.get("cleared"):
            board_after = self.board_after_cleared
        else:
            board_after = self.board_after
        self.reward_tally += coefficient * (func(board_after) - func(self.beforeState["board"]))


    def get_reward(self):

        board_after = self.board_after
        board_after_cleared = self.board_after_cleared
        board_before = self.beforeState["board"]

        # `None` board is the result of an invalid move (e.g. moving a piece out of bounds)
        if board_after is None:
             return -42_000 # Do not do this move at all

        # Compute the reward for the given state transition.

        self.reward_increase(self.empty_rows, 55, cleared=True)
        self.reward_increase(self.sum_row_fill_fractions, 20)
        self.punish_increase(self.dead_space, 30, cleared=True)
        self.punish_increase(self.bumpiness, 0.2)
        self.reward_tally += (self.score_after - self.beforeState["score"])
        self.reward_tally += self.high_score_after - self.beforeState["highScore"]
        self.reward_tally += self.num_completed_rows ** 1.5 * 10_000 # really juicy, and gets more juicier the more row we clear at a time

        return self.reward_tally


