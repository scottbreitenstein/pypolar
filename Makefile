SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs
BUILDDIR      = docs/_build

default:
	@echo Type: make check, make html, or make clean

check:
	-pyroma -d .
	-check-manifest
	make pylint
	make pep257

pylint:
	-pylint pypolar/fresnel.py
	-pylint pypolar/jones.py
	-pylint pypolar/mueller.py
	-pylint pypolar/sym_fresnel.py
	-pylint pypolar/sym_jones.py
	-pylint pypolar/sym_mueller.py
	-pylint pypolar/visualization.py

pep257:
	-pep257 pypolar/fresnel.py
	-pep257 --ignore=D401 pypolar/jones.py
	-pep257 --ignore=D401 pypolar/mueller.py
	-pep257 pypolar/sym_fresnel.py
	-pep257 --ignore=D401 pypolar/sym_jones.py
	-pep257 --ignore=D401 pypolar/sym_mueller.py
	-pep257 pypolar/visualization.py

html:
	$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

test:
	tox

clean:
	rm -rf dist
	rm -rf pypolar.egg-info
	rm -rf pypolar/__pycache__
	rm -rf docs/_build/*
	rm -rf docs/api/*
	rm -rf .tox
	
.PHONY: clean check html test