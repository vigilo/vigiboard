NAME := vigiboard
all: build

include buildenv/Makefile.common

MODULE := $(NAME)
CODEPATH := $(NAME)

lint: lint_pylint
tests: tests_tg
clean: clean_python
