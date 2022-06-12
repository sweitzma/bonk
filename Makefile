.PHONY: install
install:
	@pipx install --force .

.PHONY: dev-install
dev-install:
	@python -m venv .venv
	@. .venv/bin/activate ; pip install -e .
