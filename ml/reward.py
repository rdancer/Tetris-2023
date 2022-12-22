# reward.py - This module contains the code for defining the reward function for playing Tetris. It defines a Reward class that defines the reward function and provides methods for computing the reward for a given state.
 
def last_empty_row(board):
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
