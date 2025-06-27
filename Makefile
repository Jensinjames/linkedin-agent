.PHONY: install run

install:
	./setup.sh

run:
	python3 -m src.cli input.json
