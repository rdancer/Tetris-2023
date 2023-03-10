#!/usr/bin/env python3
# main.py -- This module contains the code for running the program to train the model. It defines a main() function that trains the model and saves the model to a file.

import os
import argparse

# Parse command-line arguments
# --off-policy: use off-policy training (true or false)
# --num-iterations: number of iterations to train for
parser = argparse.ArgumentParser()
parser.add_argument("--num-iterations", type=int, default=7500, help="number of games to play")
parser.add_argument("--url", type=str, default="http://localhost:8080", help="URL of the Tetris server")
# If we set the tick too low; the brick fall down before the model can make a prediction.
parser.add_argument("--tick", type=int, default=50, help="speed of the game [milliseconds]") # milliseconds
args = parser.parse_args()

# Silence the cretinous nagging of TensorFlow:
# "This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN) to use the following CPU instructions in performance-critical operations:  AVX2 FMA
# "To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags."
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' # Note: needs to be set before importing tensorflow

from tetris_control import Control
from model import Model

def main():
    # get the num_iterations from the command-line arguments
    with Control(args.url) as control:
        print ("Training the model...")
        model = Model(control)
        control.set_tick(args.tick)
        model.train_model(args.num_iterations)

main()