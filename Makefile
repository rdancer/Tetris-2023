.PHONY: all
all: browser server

.PHONY: server
server:
	python3 -m http.server 8000

.PHONY: browser
browser:
	open http://localhost:8000/


.PHONY: prompt_gpt
prompt_gpt:
	@echo "You have been appointed a lead developer on a Tetris game. You have been given the following code, with the assignment to make the game playable. These are the files you have:"
	@echo ' '
	@echo ' '
	@for file in index.html script.js style.css; do echo "$$file:"; echo; echo; cat "$$file"; echo; echo; done
