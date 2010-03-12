NAME := vigiboard
all: build

install:
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	mkdir -p $(DESTDIR)$(HTTPD_DIR)
	ln -f -s $(SYSCONFDIR)/vigilo/vigiboard/vigiboard.conf $(DESTDIR)$(HTTPD_DIR)/
	echo $(HTTPD_DIR)/vigiboard.conf >> INSTALLED_FILES

include buildenv/Makefile.common

MODULE := $(NAME)
CODEPATH := $(NAME)

lint: lint_pylint
tests: tests_tg
clean: clean_python
