# state.py -- This module contains the code for representing the state of the Tetris game. It defines a State class that represents the state of the game at a given point in time, and provides methods for extracting features from the state. It aims to be a thin wrapper around Control.get_state(), which itself is a thin wrapper around the JavaScript's getState() function. Ideally, the state would come from the JavaScript, and that way we could guarantee that the state that the model gets during training is the same data it gets when it runs in the browser.

import numpy as np
import tensorflow as tf

class State:
    def __init__(self, control):
        self.control = control

    def get_state(self):
        state = self.control.get_state()
        return state

    def encode_state_vector(self, state):
        """Encode the state as a vector."""
        board = np.array(state["board"])
        piece = state["piece"]

        # pad the shape so that all the shape have the same size
        shape_padded_4x4 = pad_piece_4x4(piece)

        # one-hot encode the piece type
        piece_type = np.zeros(7)
        piece_type[self.control.piece_types.index(piece["type"])] = 1

        # one-hot encode the score
        # we are interested in the model being a bit cautious when the score is high
        isHighScore = np.zeros(3)
        if state["score"] >= state["highScore"]:
            isHighScore[0] = 1
        if state["score"] >= state["highScore"] * .75:
            isHighScore[1] = 1
        if state["score"] >= state["highScore"] * .5:
            isHighScore[2] = 1

        # combine everything but the board into a single 1-D array
        state_features = np.concatenate((shape_padded_4x4.flatten(), piece_type, isHighScore))

        # combine the board and the state features into a single vector
        state = np.concatenate((board.flatten(), state_features), axis=0)

        return state.reshape(1, -1)

    def encode_state_2d(self, state):
        """
        Encode the state as a 2D array.

        Based on the approach described in (accessed 2023-01-17):
        https://www.askforgametask.com/tutorial/machine-learning/ai-plays-tetris-with-cnn/
        """
        board = np.array(state["board"])
        piece = state["piece"]

        shape_padded_4x4 = pad_piece_4x4(piece)

        # create a new 20x20 array and place the board centered in the middle
        # convolutional networks like square inputs
        board_padded = np.zeros((20, 20))
        board_padded[:, 5:15] = board
        fill_holes(board_padded)

        # place the individual pieces on the board, in the margins
        # the convolutional network loves when the pieces are spatially unique as well as shape unique
        piece_type_index = self.control.piece_types.index(piece["type"]) # ["I", "O", "T", "S", "Z", "J", "L"] : 7 types
        x_offset = 16 * (piece_type_index // 4) # either 0 or 16
        y_offset = 4 * (piece_type_index % 4) # 4 positions on the left and 3 on the right, and three spare (7 types in total)
        board_padded[y_offset:y_offset + 4, x_offset:x_offset + 4] = shape_padded_4x4

        # TODO: use the spare 4x4 slots in the lower-left corner & 8x4 slot in the lower-right corner to encode the score or other features

        # print_board(board_padded)

        return board_padded.reshape(1, 20, 20, 1)

    def encode_state(self, state):
        """Choose the encoding here."""
        return self.encode_state_2d(state)



def pad_piece_4x4(piece):
    shape = np.array(piece["shape"])
    shape_padded = np.zeros((4, 4))
    shape_padded[:shape.shape[0], :shape.shape[1]] = shape
    return shape_padded

def fill_holes(board):
    """Fill the inaccessible holes in the board. This makes in more unambiguous for the convolutional network. We do the naive thing that we do with the piece placement: no sliding sideways after drop, and we don't even move sideways during a fall under a cliff: everything below a filled cell is inaccessible."""
    for x in range(len(board[0])):
        for y in range(len(board)):
            if board[y, x] == 1:
                board[y:, x] = 1

def print_board(board):
    """Print the board."""
    print() # empty line

    # column numbers
    print("   00000000011111111112")
    print("   12345678901234567890")
    print("  +--------------------+")
    for y in range(len(board)):
        print(f"{y+1:2}", end="|")
        for x in range(len(board[0])):
            if board[y, x] == 1:
                print("X", end="")
            else:
                print(" ", end="")
        print("|") # new line
    print("  +--------------------+")