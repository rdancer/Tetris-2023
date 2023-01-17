# tetris_control.py -- This module contains the code for interacting with the Tetris game using Playwright for Python. It defines a Control class that provides methods for taking actions in the game. The Control class proxies python code to the JavaScript code runningthe Tetris game in the browser.
import time
import asyncio
from playwright.async_api import async_playwright

# Hack to get `asyncio` to work in Jupyter ("monkey patches the asyncio event loop and allows it to be re-entrant (you may calll run_until_complete while run_until_complete is already on the stack)." -- https://stackoverflow.com/a/56434301/851064)
import nest_asyncio
nest_asyncio.apply()
# __import__('IPython').embed()

class Control:
    def __init__(self, url="http://localhost:8888"):
        self.browser = None
        self.page = None
        self.browser_open = False
        self.url = url
        self.playwright = None
        self.context = None

    async def __aenter__(self):
        # print("entering Control")

        self.playwright = await async_playwright().start()

        print ("self.playwright:", self.playwright)
        # Launch a new browser
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.browser_open = True

        # Open a new page
        self.page = await self.browser.new_page()

        # Navigate to the Tetris website
        await self.page.goto(self.url)

        # Wait for the page to load
        await self.page.wait_for_selector('#game-container')

        # Wait to allow all the scripts to load and the game to start
        time.sleep(2)

        # Cache the piece types for fast access.
        self.piece_types = await self.page.evaluate("pieceTypes")

        return self

    # async def __aenter__(self):
    #     self.context = await self.playwright.new_context()
    #     self.browser = await self.context.new_browser()
    #     self.page = await self.browser.new_page()
    #     await self.page.goto(self.url)
    #     await self.page.wait_for_selector('#game-container')

    #     self.browser_open = True
    #     return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.browser_open:
            await self.browser.close()
            self.browser_open = False
        await self.playwright.stop()

    def left(self):
        # Evaluate JavaScript to call the left method on the Control class.
        asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.left()"))

    def right(self):
        # Evaluate JavaScript to call the right method on the Control class.
        asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.right()"))

    def rotate(self):
        # Evaluate JavaScript to call the rotate method on the Control class.
        asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.rotate()"))

    def down(self):
        # Evaluate JavaScript to call the down method on the Control class.
        asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.down()"))

    def drop(self):
        # Evaluate JavaScript to call the drop method on the Control class.
        asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.drop()"))

    def get_state(self):
        # Evaluate JavaScript to get the current state of the game.
        state = asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.getState()"))
        return state

    def get_piece(self):
        # Evaluate JavaScript to get the current piece.
        piece = asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.getPiece()"))
        return piece

    def get_score(self):
        # Evaluate JavaScript to get the current score.
        score = asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.getScore()"))
        return score

    def get_high_score(self):
        # Evaluate JavaScript to get the high score.
        high_score = asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.getHighScore()"))
        return high_score

    def new_game(self):
        # Evaluate JavaScript to start a new game.
        asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.newGame()"))

    def get_tick(self):
        # Evaluate JavaScript to get the current tick.
        tick = asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.getTick()"))
        return tick

    def set_tick(self, tick):
        # Evaluate JavaScript to set the current tick.
        asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.setTick(%d)" % tick))

    def is_game_over(self):
        # Evaluate JavaScript to check if the game is over.
        is_game_over = asyncio.get_event_loop().run_until_complete(self.page.evaluate("Control.isGameOver()"))
        return is_game_over