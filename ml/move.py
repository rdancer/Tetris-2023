# move.py -- abstract away the keystrokes and mouse clicks to eventuate a move
#
# There are an infinite amount of moves that can be made in Tetris. This module abstracts away the keystrokes and mouse clicks to eventuate one of the 40 possible end-states of a given move.

class Piece:
    def __init__(self, piece):
        self.piece = piece

    def get_offsets(self):
        shape = self.piece["shape"]
        offset = {}
        offset["left"] = 0
        offset["right"] = 0
        offset["top"] = 0
        offset["bottom"] = 0
        row_count = 0
        for row in shape:
            for col in row:
                if col == 1:
                    offset["left"] = min(offset["left"], col)
                    offset["right"] = max(offset["right"], col)
                    offset["top"] = min(offset["top"], row_count)
                    offset["bottom"] = max(offset["bottom"], row_count)
            row_count += 1
        # print("offset: " + str(offset))
        return offset

    def crop(self):
        shape = self.piece["shape"]
        # print("self.piece[shape]: " + str(shape))
        cropped_shape = []
        offset = self.get_offsets()
        for row in shape[offset["top"]:offset["bottom"] + 1]:
            cropped_shape.append(row[offset["left"]:offset["right"] + 1])
        # print("cropped shape: " + str(cropped_shape))            
        return cropped_shape

    def rotate(self, num_rotations):
        shape = self.crop()
        if num_rotations == 0:
            return shape
        for i in range(num_rotations):
            shape = self._rotate90(shape)
        return shape

    def _rotate90(self, shape):
        rotated_shape = []
        for col in range(len(shape[0])):
            rotated_shape.append([])
            for row in range(len(shape)):
                rotated_shape[col].append(shape[row][col])

        # print("rotated shape: " + str(rotated_shape))
        return rotated_shape
    
    def get_shape_offset(self):
        return self.get_offsets()["left"]


    @classmethod
    def get_shape_width(cls, shape):
        # max of row lengths
        return max([len(row) for row in shape])


class Move:
    def __init__(self, control):
        self.control = control
        self.possible_positions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.possible_rotations = [0, 1, 2, 3]

    def board(self):
        board = self.control.get_state()["board"]
        # make a deep copy of board
        return [row[:] for row in board]

    def piece(self):
        return self.control.get_state()["piece"]
    
    def all_possible_end_states(self):
        possible_end_states = []
        rotated_shapes = [Piece(self.piece()).rotate(rotation) for rotation in self.possible_rotations]
        for rotation in self.possible_rotations:
            shape = Piece(self.piece()).rotate(rotation)
            for position in self.possible_positions:
                # print("shape: " + str(shape) + " rotation: " + str(rotation) + " position: " + str(position))
                if Piece.get_shape_width(shape) + position <= 10:
                    result = self.simulate(position, rotation, shape)
                else:
                    result = None
                possible_end_states.append({ "board_after": result, "motion": self.construct_move(position, rotation), "position": position, "rotation": rotation })
        
        # print("possible end states: ", possible_end_states)
        return possible_end_states

    def simulate(self, xPosition, rotation, shape):
        board = self.board()
        # algorithm:
        # (1) superpose the piece on the board
        # (2) if there is a colision, return the previous board state
        # (3) else move piece down one row and repeat
        lastBoard = None
        for y in range(0, 20):
            for row in range(len(shape)):
                for col in range(len(shape[row])):
                    if shape[row][col] == 1:
                        if row + y >= 20:
                            return lastBoard
                        if board[row + y][col + xPosition] == 1:
                            return lastBoard
                        else:
                            board[row + y][col + xPosition] = 1
            lastBoard = [row[:] for row in board]

    def perform_motion(self, motion, drop = False):
        # print("motion: " + str(motion) + " drop: " + str(drop))
        for i in range(len(motion)):
            motion[i]()
        if drop:
            self.control.drop()
 
    def construct_move(self, position, rotation, drop = False):
        motion = []
        # rotate the piece
        for i in range(rotation):
            motion.append(self.control.rotate)
        # compute the moves necessary to get the uncropped piece to the desired position
        piece = self.piece()
        piece_x_origin = piece["x"]
        shape_offset = Piece(piece).get_shape_offset()
        # print("shape_offset: " + str(shape_offset) + " piece_x_origin: " + str(piece_x_origin) + " position: " + str(position))
        lateral_displacement = position
        lateral_displacement -= piece_x_origin
        lateral_displacement -= shape_offset

        if lateral_displacement > 0:
            for i in range(lateral_displacement):
                motion.append(self.control.right)
        elif lateral_displacement < 0:
            for i in range(-lateral_displacement):
                motion.append(self.control.left)
        # maybe drop the piece
        if drop:
            motion.append(self.control.drop)

        return motion



    def end_state(self, position, rotation):
        rotated_shape = Piece(self.piece()).rotate(rotation) # God, this is ineficient!
        # how far to the left can we move it? always all the way
        x_init = 0
        # how far to the right can we move it?
        x_max = 10 - Piece.get_shape_width(rotated_shape)
        board_state = [self.move(position, rotation) for position in range(x_init, x_max)]

        
    def move_sequence(self, move_sequence):
        for move in move_sequence:
            self.move(move)