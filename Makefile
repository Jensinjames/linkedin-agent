.PHONY: install run

install:
	./setup.sh

run: install
.venv/bin/python -m src.cli input.json
