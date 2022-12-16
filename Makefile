.PHONY: all
all: browser server

.PHONY: server
server:
	python3 -m http.server 8000

.PHONY: browser
browser:
	open http://localhost:8000/
