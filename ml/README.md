## tl;dr


```
npm install puppeteer && pip3 install playwright && playwright install
pip3 install tensorflowjs
pip3 install tensorflow-text tf-models-official
pip3 install asyncio nest-asyncio # if you want to train the model from a Jupyter notebook
make test && make train
# Training will run indefinitely; it can be interrupted by ^C, and restarted by running `make train` again (weights are autosaved every minute or so)
```

## Saved model & weights

The model and its associated weights are automatically saved to the files `autopilot-model.h5` and `autopilot-model-weights.h5` respectively during the training process. At the initiation of a training session, the system attempts to load any previously saved weights. Additionally, during the save process, a version of the model in TensorFlow.js format is exported to the "model/" subdirectory -- this is the version that the webpage uses.

## Changing the model

There is a Jupyter notebook `Model Experiments.ipynb` provided that allows for a quick change to the model. This is an alternative to changing the `model.py` file and running `make train` -- but each way overwrites the other's weights save file, so be careful.

## Dependencies

The repo is self-contained -- it already contains everything needed to run the code.

In order to re-train the model, you will need a few dependencies (see above).

## Auto-autopilot

To run the autopilot automatically on page load, add autopilot=true to the URL like so: [https://rdancer.github.io/Tetris-2023/?autopilot=true](https://rdancer.github.io/Tetris-2023/?autopilot=true).