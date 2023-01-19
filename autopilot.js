class Autopilot {
    constructor(autopilotButton) {
        autopilotButton.addEventListener('click', () => {
            let htmlClasses = document.querySelector('html').classList;
            htmlClasses.toggle('autopilot-enabled');
            if (htmlClasses.contains('autopilot-enabled')) {
                this.maybeLoadScript(() => this.start());
            } else {
                this.stop();
            }
        });
        this.state = new State();
        this.log = new Log();
        console.log("Autopilot loaded");
    }
    start() {
        console.log("Autopilot starting...");
        this.savedTick = Control.getTick();
        Control.setTick(50);
        this.autopilot = true;
        this.run();
    }
    stop() {
        this.autopilot = false;
        clearTimeout(this.nextScheduledRun);
        this.nextScheduledRun = null;
        Control.setTick(this.savedTick);
        console.log("Autopilot paused.");
        this.log.printStats(); // we don't want to print the stats at every step, because that would clutter the console
    }
    run() {
        if (this.autopilot) {
            this.step();
            const timeout = Control.getTick()
            this.nextScheduledRun = setTimeout(() => this.run(), timeout);
        }
    }
    step() {
        // Get the current state of the game.
        const state = this.state.getEncodedState();

        // Use the model to predict the best action.
        const prediction = this.model.predict(state);
        const action = prediction.argMax(1).dataSync()[0];

        // Action is 0..39, in the form rotation * position
        const position = action % 10;
        const rotation = Math.floor(action / 10);

        this.log.saveStats(action, position, rotation);
        
        // We don't know what the position of the piece should be, because of the left offset of the piece shape, and we are a bit lazy, so we first rotate the piece, then move it *all the way* to the first column, and then we can just move to the right by `position` steps.
        // This all happens before the piece is rendered, so it doesn't really matter.

        for (let i = 0; i < rotation; i++) Control.rotate();
        for (let i = 0; i < 9; i++) Control.left();
        for (let i = 0; i < position; i++) Control.right();

        // Drop the piece (optional).
        Control.drop();

        // Restart the game if it is over.
        if (Control.isGameOver()) {
            this.log.saveScore(Control.getState().score);
            Control.newGame();
        }
    }
    async maybeLoadScript(callback) {
        if (!this.scriptLoaded) {
            const script = document.createElement('script');
            // There are some problems with the CDN version (source map is wrong), so we use a slightly modified local version
            let tfjsUrl = 'lib/tf.js';
            script.src = tfjsUrl;
            document.head.appendChild(script);

            script.onload = async () => {
                await this.loadModel();
                callback();
            };
            this.scriptLoaded = true;
        } else {
            callback();
        }
    }
    async loadModel() {
        // "This loads a model from an http endpoint. After loading the json file the function will make requests for corresponding .bin files that the json file references" -- https://www.tensorflow.org/js/guide/save_load
        this.model = await tf.loadLayersModel('ml/model/model.json');
        console.log("Model loaded");
    }
}

class State {
    constructor() {
        // cache the pieceTypes here, for whatever that's worth
        // this.pieceTypes = Control.getPieceTypes(); // XXX doesn't work, and I cannot be bothered to fix it right now
        this.pieceTypes = ["I", "O", "T", "S", "Z", "J", "L"];
    }
    getEncodedState() {
        const state = Control.getState()
        const encodedState = this.encodeState2D(state);
        return encodedState;
    }

    //
    // following methods converted from 'state.py'
    //

    encodeState2D(state) {
        let board = state.board;
        let piece = state.piece;
    
        let shapePadded4x4 = this.padPiece4x4(piece);
    
        // create a new 20x20 array and place the board centered in the middle
        // convolutional networks like square inputs
        let boardPadded = Array(20).fill().map(() => Array(20).fill(0));
        for (let i = 0; i < board.length; i++) {
            for (let j = 0; j < board[i].length; j++) {
                boardPadded[i][j+5] = board[i][j];
            }
        }
        this.fillHoles(boardPadded);
    
        // place the individual pieces on the board, in the margins
        // the convolutional network loves when the pieces are spatially unique as well as shape unique
        let pieceTypeIndex = this.pieceTypes.indexOf(piece.type); // ["I", "O", "T", "S", "Z", "J", "L"] : 7 types
        let xOffset = 16 * Math.floor(pieceTypeIndex / 4); // either 0 or 16
        let yOffset = 4 * (pieceTypeIndex % 4); // 4 positions on the left and 3 on the right, and three spare (7 types in total)
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                boardPadded[yOffset + i][xOffset + j] = shapePadded4x4[i][j];
            }
        }
    
        // TODO: use the spare 4x4 slots in the lower-left corner & 8x4 slot in the lower-right corner to encode the score or other features
    
        // printBoard(boardPadded);

        // boardPadded has a shape (20, 20); convert it to (1, 20, 20, 1) which is the shape that the model expects
        boardPadded = boardPadded.map(row => row.map(element => [element])); // (20, 20, 1)
        const tfTensor = tf.tensor4d([boardPadded], [1, 20, 20, 1]); // (1, 20, 20, 1)
        return tfTensor;
    }
    padPiece4x4(piece) {
        let shape = piece.shape;
        let shapePadded = Array(4).fill().map(() => Array(4).fill(0));
        for (let i = 0; i < shape.length; i++) {
            for (let j = 0; j < shape[i].length; j++) {
                shapePadded[i][j] = shape[i][j];
            }
        }
        return shapePadded;
    }
    fillHoles(board) {
        // Fill the inaccessible holes in the board. This makes in more unambiguous for the convolutional network. We do the naive thing that we do with the piece placement: no sliding sideways after drop, and we don't even move sideways during a fall under a cliff: everything below a filled cell is inaccessible.
        for (let x = 0; x < board[0].length; x++) {
            for (let y = 0; y < board.length; y++) {
                if (board[y][x] === 1) {
                    for (let i = y; i < board.length; i++) {
                        board[i][x] = 1;
                    }
                    break;
                }
            }
        }
    }   
}

class Log {
    constructor() {
        this.positions = new Array(10).fill(0);
        this.rotations = new Array(4).fill(0);
        this.actionIndices = new Array(40).fill(0);
        this.actionSum = 0;
        this.totalMoves = 0;
        this.scores = [];
    }
    saveScore(score) {
        this.scores.push(score);
    }
    saveStats(action, position, rotation) {
        this.positions[position]++;
        this.rotations[rotation]++;
        this.actionIndices[action]++;
        this.actionSum += action;
        this.totalMoves++;
    }
    printStats() {
        const toPercentages = (x) => (x / this.totalMoves * 100).toFixed(2);
        console.log("average score:", (this.scores.reduce((acc, a) => acc + a, 0) / this.scores.length).toFixed(2));
        console.log("max score:", Math.max(...this.scores));
        console.log("all scores:", this.scores);
        console.log("total games:", this.scores.length);
        console.log("total moves:", this.totalMoves);
        console.log("position percentages:", this.positions.map(toPercentages));
        console.log("rotation precentages:", this.rotations.map(toPercentages));
        console.log("action percentages:", this.actionIndices.map(toPercentages));
        console.log("average action:", (this.actionSum / this.totalMoves).toFixed(2));
    }
}