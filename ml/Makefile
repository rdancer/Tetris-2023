.PHONY: train
train:
	@echo "Training model... NOT IMPLEMENTED."

.PHONY: test
test:
	@echo "Testing Control..."
	python3 ./test_playwright.py --url http://localhost:8888/

autopilot-model.json: model.h5
	tensorflowjs_converter --input_format=tf_saved_model --output_format=tfjs_graph_model model.h5 autopilot-model.json

.PHONY: train
train:
	@echo "Training model..."
	python3 ./model.py --url http://localhost:8888/
