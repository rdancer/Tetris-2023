# state.py -- This module contains the code for representing the state of the Tetris game. It defines a State class that represents the state of the game at a given point in time, and provides methods for extracting features from the state. It aims to be a thin wrapper around Control.get_state(), which itself is a thin wrapper around the JavaScript's getState() function. Ideally, the state would come from the JavaScript, and that way we could guarantee that the state that the model gets during training is the same data it gets when it runs in the browser.

import numpy as np
import tensorflow as tf

class State:
    def __init__(self, control):
        self.control = control

    def get_state(self):
        state = self.control.get_state()
        return state

    def encode_state(self, state):
        board = np.array(state["board"])
        piece = state["piece"]

        # pad the shape so that all the shape have the same size
        shape_padded_4x4 = self.pad_piece_4x4(piece)

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

    def pad_piece_4x4(self, piece):
        shape = np.array(piece["shape"])
        shape_padded = np.zeros((4, 4))
        shape_padded[:shape.shape[0], :shape.shape[1]] = shape
        return shape_padded