## tl;dr


```
npm install puppeteer && pip3 install playwright && playwright install
pip3 install tensorflowjs
pip3 install tensorflow-text tf-models-official
pip3 install asyncio nest-asyncio # if you want to train the model from a Jupyter notebook
make test && make train
# Training will run indefinitely; it can be interrupted by ^C, and restarted by running `make train` again (weights are autosaved every minute or so)
```

## Changing the model

There is a Jupyter notebook `Model Experiments.ipynb` provided that allows for a quick change to the model. This is an alternative to changing the `model.py` file and running `make train` -- but each way overwrites the other's weights save file, so be careful.

## Dependencies

The repo is self-contained -- it already contains everything needed to run the code.

In order to re-train the model, you will need a few dependencies (see above).