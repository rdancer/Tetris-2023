# Test the instrumentation of the Tetris game using Puppeteer.

from time import sleep
from tetris_control import Control

def main():
    with Control() as control:
        print ("testing Control...")
        # Use the control object to call methods on the Control class.
        control.left()
        sleep(1)
        control.right()
        sleep(1)
        control.down()
        sleep(1)
        control.down()
        sleep(1)
        control.rotate()
        sleep(1)
        control.drop()
        sleep(1)
        state = control.get_state()
        score = control.get_score()
        high_score = control.get_high_score()
        print("state: " + str(state))
        print("score: " + str(score))
        print("high score: " + str(high_score))
        sleep(5)

main()
