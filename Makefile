.PHONY: lint test

lint:
	@flake8 magiconf tests; mypy magiconf tests

test:
	pytest
