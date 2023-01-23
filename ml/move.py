# move.py -- abstract away the keystrokes and mouse clicks to eventuate a move
#
# There are an infinite amount of moves that can be made in Tetris. This module abstracts away the keystrokes and mouse clicks to eventuate one of the 40 possible end-states of a given move.

class Piece:
    def __init__(self, piece):
        self.piece = piece
        self.type = piece["type"]
        self.shape = self._crop(piece["shape"]) # discard the offsets; autopilot will just have to go 10x to the left to find out the true zero x position
        self.rotation = piece["rotation"]

    def get_shape(self):
        return self.shape

    def _crop(self, shape):
        cropped_shape = []
        offsets = self.get_offsets()
        for row in shape[offsets["top"]:len(shape) - offsets["bottom"]]:
            cropped_shape.append(row[offsets["left"]:len(shape[0]) - offsets["right"]])
        return cropped_shape

    def get_offsets(self):
        if hasattr(self, "crop_offsets"):
            return self.crop_offsets
        shape = self.piece["shape"]
        offsets = {
            # Initialise to infinities; if it stays that way, that means there is an internal error
            "left": float("inf"),
            "right": float("inf"),
            "top": float("inf"),
            "bottom": float("inf")
        }
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                value = shape[row][col]
                if value == 1:
                     offsets["left"] = min(offsets["left"], col)
                     offsets["right"] = min(offsets["right"], len(shape[row]) - 1 - col)
                     offsets["top"] = min(offsets["top"], row)
                     offsets["bottom"] = min(offsets["bottom"], len(shape) - 1 - row)
        self.crop_offsets = offsets
        return offsets

    def rotate(self, rotation):
        for i in range(((rotation + 4) - self.rotation) % 4):
            self.rotate90()
        return self.shape

    def rotate90(self):
        """Rotate a shape 90 degrees clockwise

        [1, 2, 3],
        [4, 5, 6]

        becomes

        [4, 1],
        [5, 2],
        [6, 3]"""
        self._rotate_offsets90()
        shape, rotation = self.shape, self.rotation
        rotated_shape = []
        for col in range(len(shape[0])):
            rotated_shape.append([])
            for row in range(len(shape)):
                row = len(shape) - row - 1
                rotated_shape[col].append(shape[row][col])

        # print("rotated shape: " + str(rotated_shape))
        self.shape, self.rotation = rotated_shape, (rotation + 1) % 4
        return self.shape
    
    def _rotate_offsets90(self):
        offsets = self.crop_offsets
        self.crop_offsets = {
            "top": offsets["left"],
            "right": offsets["top"],
            "bottom": offsets["right"],
            "left": offsets["bottom"]
        }

    def get_shape_width(self):
        return len(self.shape[0])

    def get_x_offset(self):
        return -self.crop_offsets["left"]


class Move:
    def __init__(self, control):
        self.control = control
        self.possible_positions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.possible_rotations = [0, 1, 2, 3]
        self.state = self.control.get_state()

    def board(self):
        return self.state["board"]

    def piece(self):
        return self.state["piece"]
    
    def all_possible_end_states(self):
        myPiece = Piece(self.piece())
        possible_end_states = []
        for rotation in self.possible_rotations:
            shape = myPiece.rotate(rotation)
            width = myPiece.get_shape_width()
            # print("shape: " + str(shape) + " width: " + str(width) + " rotation: " + str(rotation) + " x offset: " + str(myPiece.get_x_offset()))
            for position in self.possible_positions:
                if width + position <= 10:
                    board_after = self.simulate(position, rotation, shape)
                else:
                    board_after = None
                possible_end_states.append({
                    "valid": board_after != None,
                    "rotation": rotation,
                    "position": position,
                    "shape": shape,
                    "board_after": board_after,
                    "motion": self.construct_move(position, rotation)
                })
        
        # print("possible end states: ", possible_end_states)
        return possible_end_states

    def simulate(self, xPosition, rotation, shape):
        """algorithm:
        (1) superimpose the piece on the board
        (2) if there is a colision, return the previous board state
        (3) else move piece down one row and repeat"""
        lastBoard = None
        freshBoard = self.board()
        for y in range(20):
            board = [row[:] for row in freshBoard]
            for row in range(len(shape)):
                for col in range(len(shape[row])):
                    if shape[row][col] == 1:
                        if row + y >= 20 or board[row + y][col + xPosition] == 1:
                            return lastBoard
                        else:
                            board[row + y][col + xPosition] = 1
            lastBoard = board
        return lastBoard

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
        piece_x_origin = self.piece()["x"]
        piece = Piece(self.piece())
        piece.rotate(rotation) # rotate to get the right offsets
        shape_offset = piece.get_x_offset()
        lateral_displacement = position
        lateral_displacement -= piece_x_origin
        lateral_displacement += shape_offset

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
