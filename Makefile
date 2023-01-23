.PHONY: all
all: browser server

.PHONY: clean
clean:
	make -C ./ml clean
	
.PHONY: server
server:
	python3 ./http-server.py 8888

.PHONY: browser
browser:
	open http://localhost:8888/


.PHONY: prompt
prompt_gpt:
	@echo "You are a developer on a Tetris game. You have been given the following code, with the assignment:


	@echo "Use 4-column indentation in all code."
	@echo "Write all the code to implement these changes. Include comments in your code."
	@echo ' '
	@echo "These are the files you have:"
	@echo ' '
	@echo ' '
	@for file in index.html script.js style.css; do echo "$$file:"; echo; echo; cat "$$file"; echo; echo; done
