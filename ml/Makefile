# Do not print cretinous warnings
export TF_CPP_MIN_LOG_LEVEL=1

.PHONY: clean
clean:
	rm -rf autopilot-model.json
	rm -rf autopilot-model-weights.h5
	rm -rf autopilot-model/

.PHONY: test
test:
	@echo "Testing Control..."
	python3 ./test_playwright.py --url http://localhost:8888/

autopilot-model.json: autopilot-model.h5
	tensorflowjs_converter --input_format=tf_saved_model --output_format=tfjs_graph_model autopilot-model.h5 autopilot-model.json

.PHONY: train
train:
	@echo "Training model..."
	for ((i=0;;i++)); do \
		echo Epoch $$((i))...; \
		python3 ./main.py --url http://localhost:8888/; \
	done
