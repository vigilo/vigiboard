NAME = vigiboard
BUILDENV = ../glue
PYTHON = $(BUILDENV)/bin/python

all:
	@echo "Template Makefile, to be filled with build and install targets"

$(PYTHON):
	make -C $(BUILDENV) bin/python

clean:
	find $(CURDIR) \( -name "*.pyc" -o -name "*~" \) -delete
	rm -rf data # temporary: sessions

buildclean: clean
	rm -rf eggs develop-eggs parts .installed.cfg bin

apidoc: doc/apidoc/index.html
doc/apidoc/index.html: $(PYTHON) $(NAME)
	rm -rf $(CURDIR)/doc/apidoc/*
	PYTHONPATH=$(BUILDENV):src $(PYTHON) "$$(which epydoc)" -o $(dir $@) -v \
		   --name Vigilo --url http://www.projet-vigilo.org \
		   --docformat=epytext $(NAME)

lint: $(PYTHON)
	$(PYTHON) ./pylint_vigiboard.py $(NAME)

tests: $(PYTHON)
	VIGILO_SETTINGS_MODULE=settings_tests \
		PYTHONPATH=$(BUILDENV) $(BUILDENV)/bin/runtests-$(NAME)


.PHONY: all clean buildclean apidoc lint tests

