# Makefile for satisfier

SHELL := /bin/bash
HIDE ?= @
VENV ?= env
BIN_DIR ?= $(VENV)/bin

# Tools in the virtualenv
PIP ?= $(BIN_DIR)/pip
FLAKE8 ?= $(BIN_DIR)/flake8
MYPY ?= $(BIN_DIR)/mypy
PYTHON ?= $(BIN_DIR)/python

MODULE ?= satisfier

.PHONY: test
test:
	$(HIDE)$(PYTHON) -m pytest -v
	$(HIDE)$(FLAKE8) $(MODULE)
	$(HIDE)$(MYPY) $(MODULE)
