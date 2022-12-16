const gameBoard = document.getElementById("game-board");

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
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
    },
    L: {
        shape: [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0]
        ]
    }
};


const startButton = document.getElementById("start-button");
startButton.addEventListener("click", startGame);

function gridSize() { return parseInt(getComputedStyle(gameBoard).getPropertyValue("--grid-size"), 10); }

function createPieceElement(type) {
    const element = document.createElement("div");
    element.classList.add("block", type);
    return element;
}

function drawPiece(piece) {
    piece.shape.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value === 1) {
                const block = createPieceElement(piece.type);
                block.style.left = ((piece.position[1] + y) * gridSize()) + "px";
                block.style.top = ((piece.position[0] + x) * gridSize()) + "px";
                gameBoard.appendChild(block);
            }
        });
    });
}

function movePieceLeft() {
    // Update the position of the piece
}

function movePieceRight() {
    piece.position[1] += 1;
    const blocks = document.querySelectorAll(".block");
    blocks.forEach(block => {
        block.style.left = (block.offsetLeft + gridSize()) + "px";
    });
}

function movePieceDown() {
    // Update the position of the piece
}

function rotatePiece() {
    // Rotate the shape of the piece
}

// Implement the game logic
function updateGame() {
    // Check for completed rows and remove them
    // Check for game over conditions
    // Update the score
}

function startGame() {

    // Clear the game board
    gameBoard.innerHTML = "";


    // Generate a random piece
    const randomType = pieceTypes[Math.floor(Math.random() * pieceTypes.length)];
    const randomPiece = {
        position: [0, 4],
        ...pieces[randomType],
        type: randomType
    };

    // Add the piece to the game board
    drawPiece(randomPiece);
}



