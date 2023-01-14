# model.py -- This module contains the code for training and using a reinforcement learning model to play Tetris. It defines a Model class that defines the model and provides methods for training and using the model to take actions in the game.

import os
import sys


import tensorflow as tf
import numpy as np
import time
from reward import Reward
from move import Move
from state import State

MODEL_SAVE_FILE_NAME = "autopilot-model.h5"
MODEL_WEIGHTS_SAVE_FILE_NAME = "autopilot-model-weights.h5"

class stdout_redirected(object):
    def __init__(self, to="/dev/null"):
        self.to = to

    def __enter__(self):
        self.sys_stdout = sys.stdout
        sys.stdout = open(self.to, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self.sys_stdout

class Model:
  def __init__(self, control):
    self.control = control
    self.model = self.create_model()
    self.weightsLoaded = False
    self.state = State(control)

  def create_model(self):
    """Create model -- new version written by hand, now with some actual understanding of what I'm doing"""
    model = tf.keras.Sequential()

    # Comment this out so that the shape is not specified until the model is first instantiated
    # myShape = encode_state(get_state()).shape
    # model.add(tf.keras.layers.Input(input_shape=myShape))

    model.add(tf.keras.layers.Dense(1024, activation='relu'))
    model.add(tf.keras.layers.Dense(512, activation='relu'))
    model.add(tf.keras.layers.Dense(128, activation='relu'))

    numOutputs = 4 * 10 # 4 rotations × 10 positions
    model.add(tf.keras.layers.Dense(numOutputs, activation='softmax'))

    # Compile the model.
    model.compile(optimizer='adam', loss='mse')

    return model

  def train_model(self, num_iterations, offPolicy=True):
    """Train the model."""
    # Track the elapsed time.
    self.start_time = time.time()

    games_played = 0
    while games_played < num_iterations:
      if self.control.is_game_over():
        self.control.new_game()
        games_played += 1
        print ("Iteration: " + str(games_played + 1) + "/" + str(num_iterations))
        continue

      # Get the current state of the game.
      state = self.state.get_state()
      state_encoded = self.state.encode_state(state)

      # Get all the possible plays.
      move = Move(self.control)
      possible_plays = move.all_possible_end_states()
      boards_after = [play["board_after"] for play in possible_plays]
      rewards = [Reward(state, board).get_reward() for board in boards_after]
      batch_size = len(rewards) # 40
      rewards_softmax = self.softmax(np.array(rewards).reshape(1, batch_size))

      # Choose an action.
      with stdout_redirected("/dev/null"):
        prediction = self.model.predict(state_encoded)
      self.maybeLoadWeights() # We have called the model, so now the model knows its input shape, so we can load weights
      if offPolicy:
        actionChoice = np.argmax(rewards)
        assert(actionChoice == np.argmax(rewards_softmax))
      else:
        actionChoice = np.argmax(prediction)


      print("piece:", state["piece"]["type"], "position:", possible_plays[actionChoice]["position"], "rotation:", possible_plays[actionChoice]["rotation"], "reward:", rewards[actionChoice], "(" + str(rewards[np.argmax(prediction)] - rewards[np.argmax(rewards)]) + ")")

      # Take the action.
      motion = possible_plays[actionChoice]["motion"]
      move.perform_motion(motion, True)

      time.sleep(self.control.get_tick()/1000.0) # we don't collect the state after the tick, so this is just for show -- XXX there seems to be some race condition and if we don't sleep(), the training moves are weird

      # Update the model.
      with stdout_redirected("/dev/null"):
        self.model.fit(state_encoded, rewards_softmax, epochs=1, batch_size=1, verbose=0)
      self.maybeSaveWeights()

  def softmax(self, x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

  def maybeSaveWeights(self):
    """Save the model & weights to a file every minute."""
    elapsed_time = time.time() - self.start_time
    if elapsed_time >= 60:
      # Save model & weights to HDF5 files
      self.model.save(MODEL_SAVE_FILE_NAME)
      print("Saved model to file " + MODEL_SAVE_FILE_NAME)
      self.model.save_weights(MODEL_WEIGHTS_SAVE_FILE_NAME)
      print("Saved weights to file " + MODEL_WEIGHTS_SAVE_FILE_NAME)
      self.start_time = time.time()

  def maybeLoadWeights(self):
    """Load the model weights from a file if they have not already been loaded. If the file doesn't exist, do nothing."""
    if self.weightsLoaded:
      return
    self.weightsLoaded = True
    # Check if the model file exists.
    if os.path.exists(MODEL_WEIGHTS_SAVE_FILE_NAME):
      # Load weights into the model
      self.model.load_weights(MODEL_WEIGHTS_SAVE_FILE_NAME)
      print("Loaded weights from file " + MODEL_WEIGHTS_SAVE_FILE_NAME)
    else:
      print("No weights file found, starting with random weights")

    # note: only call the model summary after the model has been instantiated, so this method is a convenient place to do it
    print ("Model summary:", self.model.summary(), self.model.input_shape, self.model.output_shape)