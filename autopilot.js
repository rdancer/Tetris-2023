class Autopilot {
    constructor(autopilotButton) {
        autopilotButton.addEventListener('click', () => {
            let htmlClasses = document.querySelector('html').classList;
            htmlClasses.toggle('autopilot-enabled');
            if (htmlClasses.contains('autopilot-enabled')) {
                this.startAutopilot();
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
}