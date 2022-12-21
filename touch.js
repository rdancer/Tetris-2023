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

    let startX = 0;
    let startY = 0;
    let movedRight = 0;
    let movedLeft = 0;
    let movedUp = 0;
    let movedDown = 0;
    let swipeDetected = false;

    // Set up event listeners for all touch events
    gameBoard.addEventListener("touchstart", function (event) {
        console.log(event.type, "x:", event.touches[0].clientX, "y:", event.touches[0].clientY);
        startX = event.touches[0].clientX;
        startY = event.touches[0].clientY;
        swipeDetected = false;
    });


    // Listen for swipe events on the game board element
    gameBoard.addEventListener("touchmove", function (event) {
        console.log("Swiped", "startX:", startX, "x:", event.touches[0].clientX, "offsetX:", event.touches[0].clientX - startX, "startY:", startY, "y:", event.touches[0].clientY, "offsetY:", event.touches[0].clientY - startY);
        swipeDetected = true;
        // Call the touchMove function and pass in the x and y coordinates of the swipe event
        touchMove(event.touches[0].clientX, event.touches[0].clientY);
    });

    gameBoard.addEventListener("touchend", function (event) {
        setTimeout(200, function () {
            swipeDetected = false;
        });
    });

    let doubleTapTimeout;

    // Listen for tap events on the game board element
    gameBoard.addEventListener("touchend", function (event) {
        // Generate a synthetic spacebar event if no swipe was detected
        if (!swipeDetected) {
            if (doubleTapTimeout) {
                console.log("...Double tapped");
                clearTimeout(doubleTapTimeout);
                doubleTapTimeout = null;
                translateTouchGesturesToPieceMove("space");
            } else {
                console.log("Either tapped or double tapped...");
                doubleTapTimeout = setTimeout(200, function () {
                    console.log("...Tapped");
                    doubleTapTimeout = null;
                    translateTouchGesturesToPieceMove("up");
                });
            }
        }
        // cancel timeout doubleTapTimeout
    });

    function touchMove(x, y) {
        // Get the grid size
        const _gridSize = gridSize();

        // Get the X and Y components of the vector difference
        const xDiff = Math.round((x - startX) / _gridSize),
            yDiff = Math.round((y - startY) / _gridSize);

        console.log("xDiff:", xDiff, "y:", y, ":yDiff", yDiff, y / _gridSize, "gridSize", _gridSize)
        // Subtract the movedRight counter and add the movedLeft counter
        const xMovement = xDiff - movedRight + movedLeft;

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
        //     translateTouchGesturesToPieceMove("up");
        // }
    }

    function translateTouchGesturesToPieceMoves(key, numEvents) {
        // Generate numEvents synthetic keyboard events of the specified key
        for (let i = 0; i < numEvents; i++) {
            translateTouchGesturesToPieceMove(key);
        }
    }

    function translateTouchGesturesToPieceMove(key) {
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

    console.log("Touch events to synthetic keyboard events translation enabled.");
}