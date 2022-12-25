# model.py -- This module contains the code for training and using a reinforcement learning model to play Tetris. It defines a Model class that defines the model and provides methods for training and using the model to take actions in the game.

import os
import tensorflow as tf
from tensorflow.keras.layers import Input, concatenate, Dense, Flatten, Conv2D, MaxPooling2D, Dropout
import numpy as np
import time
from tetris_control import control as ctrl
from reward import Reward

MODEL_FILE_NAME = "autopilot-model.h5"
NUM_ITERATIONS = 42
TICK = 100 # milliseconds


control = None # global object to control the game

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

  print("returnArray shape: " + str(returnArray.shape))

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
  state_encoded_shape = encode_state(get_state()).shape
  # Define the model
  myInput = tf.keras.layers.Input(shape=state_encoded.shape)  # 2D array input layer

  # Reshape the input tensor to the desired shape
  reshaped_input = tf.keras.layers.Reshape((-1,))(myInput)

  print("input shape: " + str(reshaped_input.shape))

  # Add hidden layers with the desired number of units and activation function
  dense1 = tf.keras.layers.Dense(64, activation='relu')(reshaped_input)
  dense2 = tf.keras.layers.Dense(64, activation='relu')(dense1)

  # Add the output layer with the desired number of units and activation function
  output = tf.keras.layers.Dense(len(get_actions()), activation='softmax')(dense2)

  model = tf.keras.Model(inputs=[myInput], outputs=output)
  # Compile the model.
  model.compile(optimizer='adam', loss='mse')

  return model



def train_model(model):
  # Track the elapsed time.
  start_time = time.time()

  # Train the model.
  for i in range(NUM_ITERATIONS):
    print ("Iteration: " + str(i))
    # Get the current state of the game.
    state = get_state()
    state_encoded = encode_state(state)
    print("encoded state: " + str(state_encoded))
    piece = state["piece"]
    actions = get_actions()

    # Choose an action.
    actionChoice = np.argmax(model.predict(state_encoded)[0])

    # note: only call the model summary after the model has been instantiated
    print ("Model summary:", model.summary(), model.input_shape, model.output_shape)
    
    # Take the action.
    action = actions[actionChoice]
    action()

    time.sleep(control.get_tick()/1000.0) # as long as we wait at least a tick, the reward should be close enough
    next_state = get_state()
    reward = Reward(state, next_state, piece, action).get_reward()
    reward_encoded = np.zeros(len(actions) +2)
    reward_encoded[actionChoice] = reward

    # Update the model.
    model.fit(state_encoded, reward_encoded, epochs=1)


    # Save the model to the file every minute.
    elapsed_time = time.time() - start_time
    if elapsed_time >= 60:
      model.save(MODEL_FILE_NAME)
      print("Saved model to file " + MODEL_FILE_NAME)
      start_time = time.time()


def main():
  global control # modify the global variable
  with ctrl() as _control:
    control = _control
    print ("Training the model...")

    # Check if the model file exists.
    if os.path.exists(MODEL_FILE_NAME):
      # Load the model from the file.
      model = tf.keras.models.load_model(MODEL_FILE_NAME)
      print("Loaded model from file " + MODEL_FILE_NAME)
    else:
      # Define the model.
      model = create_model()


    control.set_tick(TICK)

    train_model(model)


main()