# tetris_control.py -- This module contains the code for interacting with the Tetris game using Playwright for Python. It defines a Control class that provides methods for taking actions in the game. The Control class proxies python code to the JavaScript code runningthe Tetris game in the browser.
import time
import argparse
from playwright.sync_api import sync_playwright


# If URL was provided as a command line argument, use it.
parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, default="https://rdancer.github.io/Tetris-2023/", help="URL to process")
args = parser.parse_args()
url = args.url


class Control:
    def __init__(self):
        self.browser = None
        self.page = None
        self.browser_open = False
        self.playwright = sync_playwright().start()
        print(self.playwright)

        # Launch a new browser
        self.browser = self.playwright.chromium.launch(headless=False)
        self.browser.open = True

        # Open a new page
        self.page = self.browser.new_page()

        # Navigate to the Tetris website
        self.page.goto(url)
        
        # Wait for the page to load
        self.page.wait_for_selector('#game-container')

        # Wait for 5 seconds to allow all the scripts to load and the game to start
        # time.sleep(5)

        # Set the flag to indicate that the browser is open
        self.browser_open = True

    def __enter__(self):
        # print("entering Control")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # print("exiting Control")
        if self.browser_open:
            self.browser.close()
            self.browser_open = False
        self.playwright.stop()

    def left(self):
        # Evaluate JavaScript to call the left method on the Control class.
        self.page.evaluate("Control.left()")

    def right(self):
        # Evaluate JavaScript to call the right method on the Control class.
        self.page.evaluate("Control.right()")

    def rotate(self):
        # Evaluate JavaScript to call the rotate method on the Control class.
        self.page.evaluate("Control.rotate()")

    def down(self):
        # Evaluate JavaScript to call the down method on the Control class.
        self.page.evaluate("Control.down()")

    def drop(self):
        # Evaluate JavaScript to call the drop method on the Control class.
        self.page.evaluate("Control.drop()")

    def get_state(self):
        # Evaluate JavaScript to get the current state of the game.
        state = self.page.evaluate("Control.getState()")
        return state
    
    def get_piece(self):
        # Evaluate JavaScript to get the current piece.
        piece = self.page.evaluate("Control.getPiece()")
        return piece

    def get_score(self):
        # Evaluate JavaScript to get the current score.
        score = self.page.evaluate("Control.getScore()")
        return score

    def get_high_score(self):
        # Evaluate JavaScript to get the high score.
        high_score = self.page.evaluate("Control.getHighScore()")
        return high_score

    def new_game(self):
        # Evaluate JavaScript to start a new game.
        self.page.evaluate("Control.newGame()")
