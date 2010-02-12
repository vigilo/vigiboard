NAME := vigiboard
MODULE := $(NAME)
CODEPATH := $(NAME)

all: build

include ../glue/Makefile.common
lint: lint_pylint
tests: tests_tg
clean: clean_python
