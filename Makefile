NAME = 

all: bin/python
	@echo "Template Makefile, to be filled with build and install targets"

bin/buildout: buildenv/bootstrap.py
	python2.5 $^

bin/python bin/paster: bin/buildout
	./$^

clean:
	find $(CURDIR) \( -name "*.pyc" -o -name "*~" \) -delete

buildclean: clean
	rm -rf eggs develop-eggs parts .installed.cfg bin

apidoc: doc/apidoc/index.html
doc/apidoc/index.html: src/vigilo
	rm -rf $(CURDIR)/doc/apidoc/*
	PYTHONPATH=src epydoc -o $(dir $@) -v \
		   --name Vigilo --url http://www.projet-vigilo.org \
		   --docformat=epytext $^

lint: bin/python
	./bin/python "$$(which pylint)" --rcfile=extra/pylintrc src/vigilo

tests:
	nosetests --with-coverage --cover-inclusive --cover-erase --cover-package vigilo tests


.PHONY: all clean buildclean apidoc lint tests

