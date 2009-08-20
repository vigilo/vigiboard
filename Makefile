NAME = vigiboard
BUILDENV = ../glue

all:
	@echo "Template Makefile, to be filled with build and install targets"

$(BUILDENV)/bin/python $(BUILDENV)/bin/paster:
	make -C $(BUILDENV) bin/python

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
	$(BUILDENV)/bin/python ./pylint_vigiboard.py $(NAME)

tests:
	PYTHONPATH=$(BUILDENV) VIGILO_SETTINGS_MODULE=settings_tests $(BUILDENV)/bin/python "$$(which nosetests)" --with-coverage --cover-inclusive --cover-erase --cover-package $(NAME) $(NAME)/tests


.PHONY: all clean buildclean apidoc lint tests

