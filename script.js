function gridSize() { return parseInt(getComputedStyle(gameBoard).getPropertyValue("--grid-size"), 10); }

const gameBoard = document.getElementById("game-board");
const startButton = document.getElementById("start-button");

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
let gameOver = false;
let gameInterval;

// Initialize game board array with empty rows
for (let i = 0; i < 20; i++) {
    gameBoardArray.push(new Array(10).fill(0));
}

// Create a new random piece
function createPiece() {
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
                if (newY > 19 || gameBoardArray[newY][currentPiece.x + x] !== 0) {
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
        if (checkGameOver()) {
            gameOver = true;
        }
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
                    currentPiece.y + y < 0 ||
                    currentPiece.y + y > 19 ||
                    gameBoardArray[currentPiece.y + y][currentPiece.x + x] !== 0
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
        row.forEach((value, x) => {
            if (value !== 0) {
                gameBoardArray[currentPiece.y + y][currentPiece.x + x] = currentPiece.type;
            }
        });
    });
}

// Check if the game is over
function checkGameOver() {
    return gameBoardArray[0].some(value => value !== 0);
}
// Update the game state and redraw the game board
function gameLoop() {
    movePieceDown();
    checkRows();
    drawBoard();
    if (gameOver) {
        clearInterval(gameInterval);
        startButton.style.display = "block";
    }
}

// Check for completed rows and remove them
function checkRows() {
    for (let y = gameBoardArray.length - 1; y >= 0; y--) {
        if (gameBoardArray[y].every(value => value !== 0)) {
            gameBoardArray.splice(y, 1);
            gameBoardArray.unshift(new Array(10).fill(0));
            score++;

            // Remove any existing block elements from the DOM
            while (gameBoard.firstChild) gameBoard.removeChild(gameBoard.firstChild);
        }
    }
}

// Clear board and reset score
function resetGame() {
    clearInterval(gameInterval);

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
            if (leftEdgeX(currentPiece) > 0 && checkCollision(currentPiece.shape, -1)) {
                currentPiece.x--;
            }
            break;
        case 39: // Right arrow
            if (rightEdgeX(currentPiece) < 9 && checkCollision(currentPiece.shape, 1)) {
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

    function columnOccupancy(piece) {
        let result = []
        for (let i = 0; i < piece.shape[0].length; i++) {
            result[i] = 0
            for (let j = 0; j < piece.shape.length; j++) {
                result[i] |= piece.shape[j][i]
            }
        }
        return result
    }
    function leftEdgeX(piece) {
        let leftOffset = columnOccupancy(piece).indexOf(1)
        let leftEdge  = piece.x + leftOffset
        return leftEdge
    }
    function rightEdgeX(piece) {
        let rightOffset = columnOccupancy(piece).reverse().indexOf(1)
        let rightEdge = piece.x + (piece.shape.length - 1) - rightOffset
        return rightEdge
    }
});

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


