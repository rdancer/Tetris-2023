function gridSize() { return parseInt(getComputedStyle(gameBoard).getPropertyValue("--grid-size"), 10); }

const gameBoard = document.getElementById("game-board");
const startButton = document.getElementById("start-button");
const pauseButton = document.getElementById("pause-button");
const scoreDisplay = document.getElementById("score-display");

const pieceTypes = ["I", "O", "T", "S", "Z", "J", "L"];

const pieces = {
    I: {
        shape: [
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0]
        ]
    },
    O: {
        shape: [
            [1, 1],
            [1, 1]
        ]
    },
    T: {
        shape: [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
    },
    S: {
        shape: [
            [0, 1, 1],
            [1, 1, 0],
            [0, 0, 0]
        ]
    },
    Z: {
        shape: [
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 0]
        ]
    },
    J: {
        shape: [
            [0, 1, 0],
            [0, 1, 0],
            [1, 1, 0]
        ]
    },
    L: {
        shape: [
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 1]
        ]
    }
};

let currentPiece;
let gameBoardArray = [];
let score = 0;
let gameInterval;

// Initialize game board array with empty rows
for (let i = 0; i < 20; i++) {
    gameBoardArray.push(new Array(10).fill(0));
}

// Create a new random piece
function createPiece() {
    if (isGameOver()) return;
    try {
        // The previous piece is no longer the current piece
        document.getElementsByClassName("current-piece")[0].classList.remove("current-piece");
    } catch (e) {}
    let type = pieceTypes[Math.floor(Math.random() * pieceTypes.length)];
    currentPiece = {
        type: type,
        x: 4,
        y: 0,
        shape: pieces[type].shape
    };
    // Check if the new piece collides with any other piece and move it upwards if it does
    while (!checkCollision(currentPiece.shape)) {
        currentPiece.y--;
    }
}

// Draw the current piece on the game board
function drawPiece() {
    // Remove current element from the game board
    const blocks = gameBoard.getElementsByClassName("current-piece");
    for (let i = blocks.length - 1; i >= 0; i--) {
        gameBoard.removeChild(blocks[i]);
    }
  
    // Add block elements for each block in the piece
    currentPiece.shape.forEach((row, y) => {
      row.forEach((value, x) => {
        if (value !== 0) {
          let block = document.createElement("div");
          block.classList.add("block", currentPiece.type, "current-piece");
          // XXX use grid-row & grid-column to position the block
          block.style.top = `${gridSize() * (currentPiece.y + y)}px`;
          block.style.left = `${gridSize() * (currentPiece.x + x)}px`;
          gameBoard.appendChild(block);
        }
      });
    });
  }
  

// Check if the current piece can move down by one row
function canMoveDown() {
    let canMove = true;
    currentPiece.shape.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                let newY = currentPiece.y + y + 1;
                if (newY > 19 || gameBoardArray[newY] && gameBoardArray[newY][currentPiece.x + x] !== 0) {
                    canMove = false;
                }
            }
        });
    });
    return canMove;
}

// Move the current piece down by one row
function movePieceDown() {
    if (canMoveDown()) {
        currentPiece.y++;
    } else {
        addPieceToBoard();
        createPiece();
    }
    drawPiece();
}

// Rotate the current piece clockwise
function rotatePiece() {
    let newShape = transpose(currentPiece.shape);
    newShape = flip(newShape);
    if (checkCollision(newShape)) {
        currentPiece.shape = newShape;
    }
    drawPiece();
}

// Transpose a matrix (turn rows into columns and columns into rows)
function transpose(matrix) {
    let newMatrix = [];
    for (let x = 0; x < matrix[0].length; x++) {
        newMatrix.push([]);
        for (let y = 0; y < matrix.length; y++) {
            newMatrix[x].push(matrix[y][x]);
        }
    }
    return newMatrix;
}

// Flip a matrix horizontally
function flip(matrix) {
    return matrix.map(row => row.reverse());
}

// Check if the current piece collides with any other pieces or the edges of the game board
function checkCollision(shape, xOffset = 0) {
    let collision = false;
    shape.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                x += xOffset
                if (
                    currentPiece.x + x < 0 ||
                    currentPiece.x + x > 9 ||
                    //currentPiece.y + y < 0 ||
                    currentPiece.y + y > 19 ||
                    gameBoardArray[currentPiece.y + y] && gameBoardArray[currentPiece.y + y][currentPiece.x + x] !== 0
                ) {
                    collision = true;
                }
            }
        });
    });
    return !collision;
}

// Add the current piece to the game board array
function addPieceToBoard() {
    currentPiece.shape.forEach((row, y) => {
        if (currentPiece.y + y < 0) return;
        row.forEach((value, x) => {
            if (value !== 0) {
                gameBoardArray[currentPiece.y + y][currentPiece.x + x] = currentPiece.type;
            }
        });
    });
}

// Check if the game is over
function isGameOver() {
    let gameOver = gameBoardArray[0].some(value => value !== 0)
    return gameOver;
}
// Update the game state and redraw the game board
function gameLoop() {
    if (isPaused()) return;
    movePieceDown();
    checkRows();
    drawBoard();
    if (isGameOver()) {
        clearInterval(gameInterval);
        document.body.classList.add("game-over");
    }
}

// Check for completed rows and remove them
function checkRows() {
    for (let y = gameBoardArray.length - 1; y >= 0; y--) {
        if (gameBoardArray[y].every(value => value !== 0)) {
            gameBoardArray.splice(y, 1);
            gameBoardArray.unshift(new Array(10).fill(0));
            score++;
            scoreDisplay.innerHTML = score;
            // Remove any existing block elements from the DOM
            while (gameBoard.firstChild) gameBoard.removeChild(gameBoard.firstChild);
        }
    }
}

// Clear board and reset score
function resetGame() {
    clearInterval(gameInterval);
    unPause()
    // Remove any existing block elements from the DOM
    while (gameBoard.firstChild) {
        gameBoard.removeChild(gameBoard.firstChild);
    }

    gameBoardArray = [];
    for (let i = 0; i < 20; i++) {
        gameBoardArray.push(new Array(10).fill(0));
    }
    score = 0;
    gameOver = false;
    document.body.classList.remove("game-over");
}

// Draw the game board
function drawBoard() {
    // Add block elements for each element in the game board array
    gameBoardArray.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                let block = document.createElement("div");
                block.classList.add("block");
                block.classList.add(value);
                block.style.top = `${gridSize() * y}px`;
                block.style.left = `${gridSize() * x}px`;
                gameBoard.appendChild(block);
            }
        });
    });
}


// Handle keyboard input
document.addEventListener("keydown", event => {
    switch (event.keyCode) {
        case 32: // Space
            while (canMoveDown()) {
                movePieceDown();
            }
            break;        
        case 37: // Left arrow
            if (new Piece(currentPiece).leftEdgeX() > 0 && checkCollision(currentPiece.shape, -1)) {
                currentPiece.x--;
            }
            break;
        case 39: // Right arrow
            if (new Piece(currentPiece).rightEdgeX() < 9 && checkCollision(currentPiece.shape, 1)) {
                currentPiece.x++;
            }
            break;
        case 40: // Down arrow
            if (canMoveDown()) {
                movePieceDown();
            }
            break;
        case 38: // Up arrow
            rotatePiece();
            break;
    }
    drawPiece();
});

function Piece(piece) {
    this.piece = piece
    this.columnOccupancy = () => {
        let result = []
        for (let i = 0; i < this.piece.shape[0].length; i++) {
            result[i] = 0
            for (let j = 0; j < this.piece.shape.length; j++) {
                result[i] |= this.piece.shape[j][i]
            }
        }
        return result
    }
    this.leftEdgeX = () => {
        let leftOffset = this.columnOccupancy(this.piece).indexOf(1)
        let leftEdge  = this.piece.x + leftOffset
        return leftEdge
    }
    this.rightEdgeX = () => {
        let rightOffset = this.columnOccupancy(this.piece).reverse().indexOf(1)
        let rightEdge = this.piece.x + (this.piece.shape.length - 1) - rightOffset
        return rightEdge
    }
    this.rowOccupancy = () => {
        let result = []
        for (let i = 0; i < this.piece.shape.length; i++) {
            result[i] = 0
            for (let j = 0; j < this.piece.shape[0].length; j++) {
                result[i] |= this.piece.shape[i][j]
            }
        }
        return result
    }
    this.topEdgeY = () => {
        let topOffset = this.rowOccupancy(this.piece).indexOf(1)
        let topEdge  = this.piece.y + topOffset
        return topEdge
    }
    this.bottomEdgeY = () => {
        let bottomOffset = this.rowOccupancy(this.piece).reverse().indexOf(1)
        let bottomEdge = this.piece.y + (this.piece.shape.length - 1) - bottomOffset
        return bottomEdge
    }
}

// Start the game
startButton.addEventListener("click", () => {
    event.preventDefault()
    event.target.blur() // lest the <Space> keypress that we use to drop the current piece depresses the button *facepalm*
    //startButton.style.display = "none";
    resetGame();
    createPiece();
    drawPiece();
    gameInterval = setInterval(gameLoop, 1000);
});


function isPaused() {
    let isPaused = document.body.classList.contains("paused")
    return isPaused
}
function unPause() {
    document.body.classList.remove("paused")
}
// Pause/resume the game
pauseButton.addEventListener("click", () => {
    event.preventDefault()
    event.target.blur() // XXX for some reason this doesn't work
    startButton.focus(); startButton.blur()  // lest the <Space> keypress that we use to drop the current piece depresses the button *facepalm*
    if (isPaused()) {
        unPause()
    } else {
        document.body.classList.add("paused")
    }
});


