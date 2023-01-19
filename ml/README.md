## tl;dr

```sh
npm install puppeteer && pip3 install playwright && playwright install
pip3 install numpy tensorflow
pip3 install tensorflowjs # you may need to pin a specific version that matches the `tensorflow` package
pip3 install asyncio nest-asyncio # if you want to train the model from a Jupyter notebook
make test && make train
# Training will run indefinitely; it can be interrupted by ^C, and restarted by running `make train` again (weights are autosaved every minute or so)
```

Our current model is a convolutional neural network, trained using supervised learning. The reward function has hand-tuned parameters, and is by no means perfect. We aim at bootstrapping by supervised learning with a low-quality reward function, then (currently unimplemented) graduate to unguided learning based on the game score only.

Tetris is a [solved problem](https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/) using a simple reward function with four parameters, which can be trained by a genetic algorithm to solve for the particular quirks of a given Tetris clone. I didn't know that when I started off. In fact, not many people know that, and GitHub is littered with half-baked projects which obviously started as attempts at solving Tetris using Neural Nets, then half-way through the project the author realised that is really a losing proposition, whereas the zero-AI approach is vastly cheaper to implement and evolve, trivial to understand, and achieves better results (see e.g. [this beautiful journey of discovery](https://www.youtube.com/watch?v=1yXBNKubb2o)). [These two Standord CS231n students](http://cs231n.stanford.edu/reports/2016/pdfs/121_Report.pdf) didn't know either, and wrote a paper about it -- their references were invaluable.

I am however undeterred in my quest to tilt at windmills, and will use this game to explore Machine Learning. I like Tetris, I like colours, and I like the way the brick fall upon each other. Autism prevails!

## Saved model & weights

The model and its associated weights are automatically saved to the files `autopilot-model.h5` and `autopilot-model-weights.h5` respectively during the training process. At the initiation of a training session, the system attempts to load any previously saved weights. Additionally, during the save process, a version of the model in TensorFlow.js format is exported to the "model/" subdirectory -- this is the version that the webpage uses.

## Jupyter notebook

There is a [Jupyter notebook](Model%20Experiments.ipynb) that allows for a quick change to the model. This is an alternative to changing the `model.py` file and running `make train` -- but each way overwrites the other's weights save file, so be careful.

## Dependencies

The repo is self-contained -- it already contains everything needed to run the code.

In order to re-train the model, you will need a few dependencies (see above).

## Auto-autopilot

To run the autopilot automatically on page load, add autopilot=true to the URL like so: [https://rdancer.github.io/Tetris-2023/?autopilot=true](https://rdancer.github.io/Tetris-2023/?autopilot=true).