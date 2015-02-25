PYTHON ?= python
NOSE = $(PYTHON) -m nose
PYLINT = $(PYTHON) -m pylint
PEP8 = $(PYTHON) -m pep8

TESTDIRS = typesafety/

.PHONY: pre-commit
pre-commit: codingstandards check

.PHONY: pre-merge
pre-merge: pre-commit documentation

.PHONY: check
check:
	$(NOSE) --with-coverage --with-doctest -s $(TESTDIRS)

.PHONY: codingstandards
codingstandards: check-copyright
	$(PEP8) --repeat $(TESTDIRS)
	$(PYLINT) -f parseable --rcfile=.pylintrc $(TESTDIRS)

.PHONY: documentation
documentation:
	make -C doc html

.PHONY: check-copyright
check-copyright:
	./scripts/copyright.py --check .

.PHONY: update-copyright
update-copyright:
	./scripts/copyright.py --update .
