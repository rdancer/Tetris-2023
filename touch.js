function TranslateTouchEventsToSyntheticKeyboardEvents(gameBoard) {
    // log to #console on mobile devices
    console._log = console.log;
    console.log = function () {
        console._counter ??= 0;
        console._log(...arguments);
        var consoleDiv = document.getElementById("console");
        consoleDiv.innerHTML += `${console._counter++}: ` + Array.from(arguments).join(" ") + "<br>";
        consoleDiv.lastChild.scrollIntoView();
    };

    let startX;
    let startY;
    let movedRight;
    let movedLeft;
    let movedUp;
    let movedDown;
    let swipeDetected;

    // Set up event listeners for all touch events
    gameBoard.addEventListener("touchstart", function (event) {
        console.log(event.type, "x:", event.touches[0].clientX, "y:", event.touches[0].clientY);
        startX = event.touches[0].clientX;
        startY = event.touches[0].clientY;
        movedRight = 0;
        movedLeft = 0;
        movedUp = 0;
        movedDown = 0;
        swipeDetected = false;
    });


    // Listen for swipe events on the game board element

    // Maybe it's a swipe
    gameBoard.addEventListener("touchmove", function (event) {
        console.log("Swiped", "startX:", startX, "x:", event.touches[0].clientX, "offsetX:", event.touches[0].clientX - startX, "startY:", startY, "y:", event.touches[0].clientY, "offsetY:", event.touches[0].clientY - startY);
        swipeDetected = true;
        // Call the touchMove function and pass in the x and y coordinates of the swipe event
        touchMove(event.touches[0].clientX, event.touches[0].clientY);
    });

    // If it is not a swipe, maybe it's a tap
    gameBoard.addEventListener("touchend", function (event) {
        // Generate a synthetic spacebar event if no swipe was detected
        if (!swipeDetected) {
            translateTouchGesturesToPieceMoves("up");
        };
        swipeDetected = false;
    });

    function touchMove(x, y) {
        // Get the grid size
        const _gridSize = gridSize();

        // Get the number of grid squares the swipe is displaced horizontally and vertically
        const xGridDiff = Math.round((x - startX) / _gridSize),
            yGridDiff = Math.round((y - startY) / _gridSize);

        console.log("xGridDiff:", xGridDiff, "y:", y, "yGridDiff:", yGridDiff, "gridSize:", _gridSize)
        // Subtract the movedRight counter and add the movedLeft counter
        const xMovement = xGridDiff - movedRight + movedLeft;

        // If the result is negative n, send n left-arrow synthetic keyboard events
        if (xMovement < 0) {
            translateTouchGesturesToPieceMoves("left", -xMovement);
        }
        // Else if the result is positive n, send n right-arrow synthetic keyboard events
        else if (xMovement > 0) {
            translateTouchGesturesToPieceMoves("right", xMovement);
        }

        // Analogously, from the vertical displacement, and taking into account
        // how many up arrow and down arrow events have been sent, send m synthetic up/down arrow events
        // const yMovement = Math.abs(yDiff);
        // if (yMovement > 1) {
        //     console.log(`translateTouchGesturesToPieceMoves("up")`);
        //     translateTouchGesturesToPieceMoves("up");
        // }
    }

    function translateTouchGesturesToPieceMoves(key, numEvents = 1) {
        for (let i = 0; i < numEvents; i++) {
            console.log("translating move:", key);
            switch (key) {
                case 'left':
                    movedLeft++;
                    Control.left();
                    break;
                case 'right':
                    movedRight++;
                    Control.right();
                    break;
                case 'up':
                    movedUp++;
                    Control.up();
                    break;
                case 'down':
                    movedDown++;
                    Control.down();
                    break;
                case 'space':
                    Control.space();
                    break;
            }
            drawPiece();
        }
    }

    console.log("Touch events to synthetic keyboard events translation enabled.");
}