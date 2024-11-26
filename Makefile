.PHONY: lint format test install clean
.SILENT: lint format clean all run init

lint:
	ruff check . --fix || true
	mypy . || true

format:
	ruff format .

