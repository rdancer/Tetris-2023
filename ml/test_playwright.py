# Test the instrumentation of the Tetris game using Puppeteer.

from time import sleep
from tetris_control import Control

def main():
    with Control() as control:
        print ("testing Control...")
        attempts = 0

        # Get the right shape, so that the test is reproducible. This can take a while.
        while control.get_state()["piece"]["type"] != 'T':
            attempts += 1
            control.new_game()

        print("got the T piece in " + str(attempts) + " attempts")

        control.left()
        # sleep(1)
        control.right()
        # sleep(1)
        control.down()
        # sleep(1)
        control.down()
        # sleep(1)
        control.rotate()
        # sleep(1)
        control.drop()
        tetromino = control.get_piece()
        sleep(2) # wait one tick and a bit for the board array to update
        stateAfterDrop = control.get_state()
        score = control.get_score()
        high_score = control.get_high_score()
        # print("piece: " + str(tetromino))
        # print("state after drop: " + str(stateAfterDrop))
        # print("score: " + str(score))
        # print("high score: " + str(high_score))
        # sleep(3)

        # test if the piece looks like our precomputed piece
        assert tetromino == {'type': 'T', 'x': 4, 'y': 17, 'shape': [[0, 1, 0], [0, 1, 1], [0, 1, 0]]}
        assert stateAfterDrop["board"] == [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]
        assert score == 0
        assert high_score == 0

        print("test PASSED")
        return 0

main()
