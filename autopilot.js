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
            switch (action) {
                case 0:
                    Control.left();
                    break;
                case 1:
                    Control.right();
                    break;
                case 2:
                    Control.down();
                    break;
                case 3:
                    Control.rotate();
                    break;
                case 4:
                    Control.drop();
                    break;
            }

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
