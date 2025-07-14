.PHONY: install run

install:
./setup.sh

run:
.venv/bin/python -m src.cli input.json
