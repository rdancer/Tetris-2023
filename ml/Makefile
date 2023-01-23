# Do not print cretinous warnings
export TF_CPP_MIN_LOG_LEVEL=1

SCHEDULING_PRIORITY_WHEN_TRAINING = 10

.PHONY: clean
clean:
	rm -rf autopilot-model.json
	rm -rf autopilot-model-weights.h5
	rm -rf autopilot-model/

.PHONY: test
test:
	@echo "Testing Control..."
	python3 ./test_playwright.py --url http://localhost:8888/

.PHONY: autopilot-model-json
autopilot-model-json: autopilot-model.h5
	# The last argument is the save *directory*. The output file name is hardcoded.
	tensorflowjs_converter --input_format=keras --output_format=tfjs_graph_model ./autopilot-model.h5 ./model

.PHONY: train
train:
	@echo "Training model..."
	for ((i=0;;i++)); do \
		echo Epoch $$((i))...; \
		nice -n $(SCHEDULING_PRIORITY_WHEN_TRAINING) python3 ./main.py --url http://localhost:8888/; \
	done
