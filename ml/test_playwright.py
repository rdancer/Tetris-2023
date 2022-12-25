# Test the instrumentation of the Tetris game using Puppeteer.

from time import sleep
from tetris_control import control as ctrl

def main():
    with ctrl() as control:
        print ("testing Control...")
        attempts = 0

        # Get the right shape, so that the test is reproducible. This can take a while.
        while control.get_state()["piece"]["type"] != 'T':
            attempts += 1
            control.new_game()

        print("got the T piece in " + str(attempts) + " extra attempts")

        tick = 300 # milliseconds
        control.set_tick(tick)
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
        sleep(2*tick/1000) # wait one tick and a bit for the board array to update
        stateAfterDrop = control.get_state()
        score = control.get_score()
        high_score = control.get_high_score()
        # print("piece: " + str(tetromino))
        # print("state after drop: " + str(stateAfterDrop))
        # print("score: " + str(score))
        # print("high score: " + str(high_score))
        # sleep(3*tick)

        # test if the state looks like our precomputed state
        assert tetromino == {'type': 'T', 'x': 4, 'y': 17, 'shape': [[0, 1, 0], [0, 1, 1], [0, 1, 0]], 'rotation': 1}
        assert stateAfterDrop["board"] == [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]
        assert score == 0
        assert high_score == 0
        assert control.get_tick() == tick

        print("test PASSED")
        return 0

main()
