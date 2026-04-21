PKG 	   := $(shell basename $(PWD))
PYTHON	   := python
PIP    	   := $(PYTHON) -m pip
PYTEST 	   := $(PYTHON) -m pytest -v

install:
	$(PIP) install .

develop:
	$(PIP) install -e .

check: with-pytest
	$(PYTEST) tests

uninstall:
	$(PIP) uninstall --yes $(PKG)

clean:
	@rm -rf build src/*.egg-info
	@find . -depth -type d -name __pycache__ -exec rm -rf '{}' ';'


# helpers

with-%:
	@$(PYTHON) -c "import $*" 2>/dev/null || $(PIP) install $*

