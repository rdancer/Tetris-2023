class Autopilot {
    constructor(autopilotButton) {
        autopilotButton.addEventListener('click', () => {
            let htmlClasses = document.querySelector('html').classList;
            htmlClasses.toggle('autopilot-enabled');
            if (htmlClasses.contains('autopilot-enabled')) {
                this.maybeLoadScript(() => this.startAutopilot());
            } else {
                this.stopAutopilot();
            }
        });
        console.log("Autopilot loaded");
    }
    startAutopilot() {
        console.log("Autopilot starting...");
        this.autopilot = true;

        while (this.autopilot) {
            // Get the current state of the game.
            const state = Control.getState();

            // Use the model to predict the best action.
            const action = model.predict(state);

            // Take the action.
            // Action is 0..39, in the form rotation * position
            const position = action % 4;
            const rotation = Math.floor(action / 10);

            // we don't know what the position of the piece should be, because of left offset of the piece shape, and we are a bit lazy, so what we do is to first rotate the piece, then move *all the way* to the first column, and then we can just move to the right by `position` steps

            // XXX FIXME this is visually quite unappealing, because the piece just jumps to the new position; we shold make it more cinematic, by rotating and moving the piece one step at a time, and only as necessary

            for (let i = 0; i < rotation; i++) {
                Control.rotate();
            }
            for (let i = 0; i < 9; i++) {
                Control.left();
            }
            for (let i = 0; i < position; i++) {
                Control.right();
            }

            // Optionally drop the piece.
            //Control.drop();

            // Restart the game if it is over.
            if (Control.gameOver()) {
                Control.newGame();
            }
        }
    }
    stopAutopilot() {
        this.autopilot = false;
        console.log("Autopilot paused.");
    }
    async maybeLoadScript(callback) {
        if (!this.scriptLoaded) {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@2.6.0/dist/tf.min.js';
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
        const model = await tf.loadGraphModel('ml/autopilot-model.json');
        console.log("Model loaded");
    }
}
