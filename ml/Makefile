.PHONY: train
train:
	@echo "Training model... NOT IMPLEMENTED."

.PHONY: test
test:
	@echo "Testing Control..."
	python3 ./test_playwright.py --url http://localhost:8888/
	@[ $$? -eq 0 ] && echo "Test PASSED."

autopilot-model.json: autopilot-model.pb
	tensorflowjs_converter --input_format=tf_saved_model --output_format=tfjs_graph_model autopilot-model.pb autopilot-model.json
