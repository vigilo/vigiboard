NAME = vigiboard

all: bin/python
	@echo "Template Makefile, to be filled with build and install targets"

bin/buildout: buildenv/bootstrap.py
	http_proxy='' HTTP_PROXY='' python2.5 $^
	-[ -f $@ ] && touch $@

bin/python bin/paster: bin/buildout
	http_proxy='' HTTP_PROXY='' ./$^

clean:
	find $(CURDIR) \( -name "*.pyc" -o -name "*~" \) -delete

buildclean: clean
	rm -rf eggs develop-eggs parts .installed.cfg bin

apidoc: doc/apidoc/index.html
doc/apidoc/index.html: $(NAME)
	rm -rf $(CURDIR)/doc/apidoc/*
	PYTHONPATH=src epydoc -o $(dir $@) -v \
		   --name Vigilo --url http://www.projet-vigilo.org \
		   --docformat=epytext $^

lint:
	./pylint_vigiboard.py $(NAME)

tests:
	nosetests --with-coverage --cover-inclusive --cover-erase --cover-package $(NAME) tests


.PHONY: all clean buildclean apidoc lint tests

