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
        console.log("Autopilot starting... ... not implemented.");
    }
    stopAutopilot() {
        console.log("Autopilot stopping... ... not implemented.");
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
