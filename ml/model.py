# model.py -- This module contains the code for training and using a reinforcement learning model to play Tetris. It defines a Model class that defines the model and provides methods for training and using the model to take actions in the game.

import os
import sys
import tensorflow as tf
from tensorflow.keras.layers import Input, concatenate, Dense, Flatten, Conv2D, MaxPooling2D, Dropout
import numpy as np
import time
from tetris_control import control as ctrl
from reward import Reward
from move import Move

MODEL_WEIGHTS_SAVE_FILE_NAME = "autopilot-model-weights.h5"
NUM_ITERATIONS = 42
TICK = 100 # milliseconds


control = None # global object to control the game


class stdout_redirected(object):
    def __init__(self, to="/dev/null"):
        self.to = to

    def __enter__(self):
        self.sys_stdout = sys.stdout
        sys.stdout = open(self.to, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self.sys_stdout



# Define the state space.
def get_state():
  state = control.get_state()
  return state

def encode_state(state):
  return np.array([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1.]])

def foobar():
  board = np.array(state["board"])
  piece = state["piece"]

  # pad the shape so that all the shape have the same size
  pad_piece_4x4(piece)

  # one-hot encode the piece type
  piece_type = np.zeros(7)
  piece_type[control.piece_types.index(piece["type"])] = 1

  # one-hot encode the piece rotation
  piece_rotation = np.zeros(4)
  piece_rotation[piece["rotation"]] = 1

  # one-hot encode the piece x position
  piece_x_position = np.zeros(10)
  piece_x_position[piece["x"]] = 1

  # one-hot encode the piece y position
  piece_y_position = np.zeros(20)
  piece_y_position[piece["y"]] = 1
  
  # one-hot encode the score
  # we are interested in the model being a bit cautious when the score is high, so encode a one-bit values for the score
  # We need 40 bits, and only have 38 so far, so expand the score to 3 bits
  isHighScore = np.zeros(3)
  if state["score"] >= state["highScore"]:
    isHighScore[0] = 1
  if state["score"] >= state["highScore"] * .75:
    isHighScore[1] = 1
  if state["score"] >= state["highScore"] * .5:
    isHighScore[2] = 1

  # combine everything but the board into a single 1-D array
  combinedArray = concatenate_arrays((piece["shape"], piece_type, piece_rotation, piece_x_position, isHighScore))

  # reshape the flattened array so that it can be concatenated with the board
  combinedArray = np.reshape(combinedArray, (20, 2))

  # concatenate the board and the combined array
  returnArray = np.hstack((board, combinedArray))

  # print("returnArray shape: " + str(returnArray.shape))

  return returnArray


def concatenate_arrays(arrays):
  """
  Concatenate a list of 1D or 2D arrays with a 2D array and return the resulting array.
  
  Parameters:
  - board: 2D list
    The 2D array to concatenate the 1D or 2D arrays with.
  - arrays: list of 1D or 2D lists
    The list of 1D or 2D arrays to concatenate with the 2D array.
  """
  # Convert the input arrays to NumPy arrays
  arrays = [np.array(array) for array in arrays]

  # Flatten the arrays
  arrays = [array.flatten() for array in arrays]

  # Concatenate the arrays along the first axis
  concatenated_array = np.concatenate(arrays)

  return concatenated_array



def pad_piece_4x4(piece):
  """Pad a piece to 4x4, if necessary. This is necessary because the piece can be smaller than 4x4. The padding is done on the right and bottom. The padding is done with zeros. This is necessary because the model needs all pieces to be the same size. This function modifies the piece in place. Returns the piece."""
  pad_width = ((0, 4 - len(piece["shape"])), (0, 4 - len(piece["shape"][0])))
  piece["shape"] = np.pad(piece["shape"], pad_width, 'constant', constant_values=0)
  return piece

# Define the action space.
def get_actions():
  return [control.left, control.right, control.down, control.rotate, control.drop]

def create_model():
  """Create model -- new version written by hand, now with some actual understanding of what I'm doing"""
  model = tf.keras.Sequential()

  # Comment this out so that the shape is not specified until the model is first instantiated
  # myShape = encode_state(get_state()).shape
  # model.add(tf.keras.layers.Input(input_shape=myShape))

  model.add(tf.keras.layers.Dense(64, activation='relu'))
  model.add(tf.keras.layers.Dense(64, activation='relu'))

  model.add(tf.keras.layers.Dense(len(get_actions()), activation='softmax'))

  # Compile the model.
  model.compile(optimizer='adam', loss='mse')

  return model

def create_model_XXX_DNW():
  """Create the model."""
  # Define the model
  myInput = tf.keras.layers.Input(40) # 1 input per rotation x column

  # Reshape the input tensor to the desired shape
  # reshaped_input = tf.keras.layers.Reshape((-1,))(myInput)

  # print("input shape: " + str(reshaped_input.shape))

  # Add hidden layers with the desired number of units and activation function
  dense1 = tf.keras.layers.Dense(64, activation='relu')(myInput)
  dense2 = tf.keras.layers.Dense(64, activation='relu')(dense1)

  # Add the output layer with the desired number of units and activation function
  output = tf.keras.layers.Dense(len(get_actions()), activation='softmax')(dense2)

  model = tf.keras.Model(inputs=[myInput], outputs=output)
  # Compile the model.
  model.compile(optimizer='adam', loss='mse')

  return model

def create_constant_model():
  """Create a dummy model that always returns a constant value."""
  myInput = tf.keras.layers.Input(shape=(20,10))  # 2D array input layer
  # Create a constant tensor with the desired shape
  output = tf.constant([[24]], dtype=tf.float32)

  # Create a Lambda layer that wraps the constant tensor and returns it as the output
  output_layer = tf.keras.layers.Lambda(lambda x: output)(myInput)

  # Define the model with the Lambda layer as the output
  model = tf.keras.Model(inputs=myInput, outputs=output_layer)
  model.compile(optimizer='adam', loss='mse')

  return model

def train_model(model):
  # Track the elapsed time.
  start_time = time.time()

  # Train the model.
  gamesRemaining = NUM_ITERATIONS
  while gamesRemaining > 0:
    # Get the current state of the game.
    state = get_state()
    state_encoded = encode_state(state)
    # print("encoded state: " + str(state_encoded))
    piece = state["piece"]

    if control.is_game_over():
      control.new_game()
      gamesRemaining -= 1
      print ("Iteration: " + str(NUM_ITERATIONS - gamesRemaining))
      continue

    # Get all the possible plays.
    myMove = Move(control)
    possible_plays = myMove.all_possible_end_states()
    # print ("possible_plays:", len(possible_plays))
    boards_after = [play["board_after"] for play in possible_plays]
    # print ("boards_after:", len(boards_after))
    _boards = []
    badBoardCount = 0
    for board in boards_after:
      # print("board type:", type(board))
      # if board is NoneType, then it's a bad board and we should skip it
      if board is None:
        badBoardCount += 1
        # print("XXXXXXXXXXXXX board is None and not good XXXXXXXXXXXXXXX")
        # print("substituting a dummy board for now")
        # Create a dummy board XXX this is really bad
        board = [[0 for x in range(10)] for y in range(20)]
        _boards.append(board)
        continue
      # print("board[0] type:", type(board[0]))
      # print("board shape: " + str(len(board)) + " x " + str(len(board[0])))
      _boards.append(board)
    boards_after = _boards
    print(badBoardCount, "dummy boards") # XXX the count is never zero, no need for a conditionsl unfortunately
    np_boards_after = np.array([np.array(board) for board in _boards])
    rewards = [Reward(state, board).get_reward() for board in boards_after]
    batch_size = len(rewards) # 40
    rewards = np.array(rewards)
    rewards = rewards.reshape((batch_size, 1)) # Fixes: Incompatible shapes: [39,20,5] vs. [39]

    # note: only call the model summary after the model has been instantiated
    # print ("Model summary:", model.summary(), model.input_shape, model.output_shape)

    # Choose an action.
    with stdout_redirected("/dev/null"):
      prediction = model.predict(np_boards_after)[0]

    actionChoice = np.argmax(prediction)
    # print ("XXXXXXXX ignore the model's choice of action for now and do the one that got the biggest Reward XXXXXXXXXX")
    actionChoice = np.argmax(rewards)

    # print ("rewards:", rewards)    
    print("position:", possible_plays[actionChoice]["position"], "rotation:", possible_plays[actionChoice]["rotation"], "reward:", rewards[actionChoice])

    # Take the action.
    motion = possible_plays[actionChoice]["motion"]
    myMove.perform_motion(motion, True)

    time.sleep(control.get_tick()/1000.0) # as long as we wait at least a tick, the reward should be close enough

    # Update the model.
    with stdout_redirected("/dev/null"):
      model.fit(np_boards_after, rewards, epochs=1, batch_size=batch_size)

    # Save the model to the file every minute.
    elapsed_time = time.time() - start_time
    if elapsed_time >= 60:
      # Save model weights to HDF5 file
      model.save_weights(MODEL_WEIGHTS_SAVE_FILE_NAME)
      print("Saved model to file " + MODEL_WEIGHTS_SAVE_FILE_NAME)
      start_time = time.time()


def main():
  global control # modify the global variable
  with ctrl() as _control:
    control = _control
    print ("Training the model...")

    # Define the model.
    # model = create_model()
    model = create_constant_model()

    # Check if the model file exists.
    if os.path.exists(MODEL_WEIGHTS_SAVE_FILE_NAME):
      # Load weights into the model
      model.load_weights(MODEL_WEIGHTS_SAVE_FILE_NAME)



    control.set_tick(TICK)

    train_model(model)


main()