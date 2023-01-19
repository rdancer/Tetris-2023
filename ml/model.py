# model.py -- This module contains the code for training and using a reinforcement learning model to play Tetris. It defines a Model class that defines the model and provides methods for training and using the model to take actions in the game.

import os
import sys


import tensorflow as tf
import numpy as np
import time
from reward import Reward
from move import Move
from state import State
import math
import tensorflowjs as tfjs # For saving the model in a format that can be used in the browser

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
    self.state = State(control)

  def create_model_simple(self):
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

  def create_model(self):
    """Convolutional 2D model that takes padded board + embedded piece shapes as input and outputs one of the 40 actions"""
    model = tf.keras.Sequential()

    # Comment this out so that the shape is not specified until the model is first instantiated
    # myShape = encode_state(get_state()).shape
    # model.add(tf.keras.layers.Input(input_shape=myShape))

    model.add(tf.keras.layers.Conv2D(128, (3, 3), activation='relu', input_shape=(20, 20, 1)))
    # model.add(tf.keras.layers.MaxPooling2D((2, 2)))
    model.add(tf.keras.layers.Conv2D(96, (3, 3), activation='relu'))
    # model.add(tf.keras.layers.MaxPooling2D((2, 2)))
    model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(64, activation='relu'))

    numOutputs = 4 * 10
    model.add(tf.keras.layers.Dense(numOutputs, activation='softmax'))

    # Compile the model.
    model.compile(optimizer='adam', loss='mse')

    return model

  def train_model(self, num_iterations, epsilon=1):
    """Train the model."""
    epsilon_delta = (0.95 - epsilon) / num_iterations
    self.autoSaver = AutoSaver(self.model)
    games_played = 0
    total_reward = 0
    reward_history = []
    state_history = []
    print ("Iteration: " + str(games_played + 1) + "/" + str(num_iterations))
    while games_played < num_iterations:
      if self.control.is_game_over():
        self.replay(total_reward, reward_history, state_history, epsilon)
        epsilon += epsilon_delta
        self.control.new_game()
        games_played += 1
        if games_played < num_iterations:
          print ("Iteration: " + str(games_played + 1) + "/" + str(num_iterations))
          total_reward = 0
          reward_history = []
          state_history = []
        else:
          print ("Training complete.")
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
      self.autoSaver.maybeLoadWeights() # We have called the model, so now the model knows its input shape, so we can load weights
      if epsilon < np.random.rand():
        actionChoice = np.argmax(rewards)
        assert(actionChoice == np.argmax(rewards_softmax))
      else:
        actionChoice = np.argmax(prediction)


      # print("piece:", state["piece"]["type"], "position:", possible_plays[actionChoice]["position"], "rotation:", possible_plays[actionChoice]["rotation"], "reward:", rewards[actionChoice], "(" + str(rewards[np.argmax(prediction)] - rewards[np.argmax(rewards)]) + ")")

      # Take the action.
      motion = possible_plays[actionChoice]["motion"]
      move.perform_motion(motion, True)

      # time.sleep(self.control.get_tick()/1000.0) # we don't collect the state after the tick, so there is only one problem: XXX if we don't sleep, we will evaluate the same tetromino more than once, because the nextPiece() call will not have happened yet -- this is fine for off-policy with no memory, but once we are doing reinforcement learning with history, we will need to sync.
      # TODO Registering a callback with the control object might be the way to go.

      # Evaluate the action.
      model_choice_index = np.argmax(prediction)
      model_choice_reward = rewards[model_choice_index]
      total_reward += model_choice_reward
      reward_history.append(model_choice_reward)
      state_history.append(state_encoded)

      # Update the model.
      with stdout_redirected("/dev/null"):
        self.model.fit(state_encoded, rewards_softmax, epochs=1, batch_size=1, verbose=0)
      self.autoSaver.maybeSaveWeights()

  def replay(self, total_reward, reward_history, state_history, epsilon, discount_factor=0.95):
    """Replay the game and train the model."""
    print("Replaying game with epsilon = " + str(epsilon), "total reward = " + str(total_reward), "discount factor = " + str(discount_factor))
    print("Game length: " + str(len(reward_history)))

    # how many states do we want to look ahead -- Nth state to influence the reward by 1%
    lookAhead = int(math.log(1/100, discount_factor))
    print ("Look ahead: " + str(lookAhead))

    # Tetris being a solved problem, we should never really be in a state where we have no moves left, so we can just disregard the end-game.

    print("Ignoring endgame states: %.2f%% of total game length" % (lookAhead / len(reward_history) * 100))
    for i in range(len(reward_history) - lookAhead):
      for j in range(lookAhead):
        reward_history[i] += discount_factor ** j * reward_history[i+j]

    # XXX we don't know how to weigh the rewards for the actions that did not get chosen, though
    # XXX use gradient tape??
    print("Training model... XXXXXX Does not work, skipping XXXXXX")
    # self.model.fit(state_history, reward_history, epochs=1, batch_size=1, verbose=0)

  def softmax(self, x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

class AutoSaver:
  """This class provides methods for saving and loading the model weights to/from a file."""

  MODEL_SAVE_FILE_NAME = "autopilot-model.h5"
  MODEL_JSON_SAVE_DIR = "./model/"
  MODEL_WEIGHTS_SAVE_FILE_NAME = "autopilot-model-weights.h5"

  def __init__(self, model):
    self.model = model
    self.weightsLoaded = False

  def maybeSaveWeights(self):
    """Save the model & weights to a file every minute."""
    if not hasattr(self, 'start_time'):
      self.start_time = time.time()
    elapsed_time = time.time() - self.start_time
    if elapsed_time >= 60:
      # Save model & weights to HDF5 files
      self.model.save(self.MODEL_SAVE_FILE_NAME)
      print("Saved model to file " + self.MODEL_SAVE_FILE_NAME)
      tfjs.converters.save_keras_model(self.model, self.MODEL_JSON_SAVE_DIR)
      print("Saved JSON model to directory " + self.MODEL_JSON_SAVE_DIR)
      self.model.save_weights(self.MODEL_WEIGHTS_SAVE_FILE_NAME)
      print("Saved weights to file " + self.MODEL_WEIGHTS_SAVE_FILE_NAME)
      self.start_time = time.time()

  def maybeLoadWeights(self):
    """Load the model weights from a file if they have not already been loaded. If the file doesn't exist, do nothing."""
    if self.weightsLoaded:
      return
    self.weightsLoaded = True
    # Check if the model file exists.
    if os.path.exists(self.MODEL_WEIGHTS_SAVE_FILE_NAME):
      # Load weights into the model
      try:
        self.model.load_weights(self.MODEL_WEIGHTS_SAVE_FILE_NAME) # This will fail if the model has been changed since the weights were saved
        print("Loaded weights from file " + self.MODEL_WEIGHTS_SAVE_FILE_NAME)
      except:
        print("Weights file found, but failed to load weights (most likely model has changed since last save) -- starting with random weights and will overwrite weights file")
    else:
      print("No weights file found, starting with random weights")

    # note: only call the model summary after the model has been instantiated, so this method is a convenient place to do it
    print ("Model summary:", self.model.summary(), self.model.input_shape, self.model.output_shape)