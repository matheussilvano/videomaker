.PHONY: setup check test lint fmt types demo doctor
setup:        ## install deps, browser and narration models
	uv sync --all-extras --group dev
	uv run videomaker setup --browser --models
check: lint types test   ## everything CI runs
test:
	uv run pytest -q
lint:
	uv run ruff check src tests
	uv run ruff format --check src tests
fmt:
	uv run ruff format src tests
	uv run ruff check --fix src tests
types:
	uv run mypy src
demo:         ## build the demo video
	uv run videomaker build examples/demo-en/storyboard.json -o out/demo
doctor:
	uv run videomaker doctor
