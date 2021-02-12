SHELL=/usr/bin/env bash
# .DEFAULT_GOAL := check_all
# PYTHON_PACKAGE_NAME = blackjack
python_files := $(shell find . -type f -name '*.py')
# git_files := $(shell git ls-tree --name-only -r HEAD)


.PHONY: test
test: pyproject.toml $(python_files)
	poetry run pytest

.PHONY: sort_imports
split_string = $(firstword $(subst , ,$1))
sort_imports: pyproject.toml $(python_files)
	poetry run isort \
		--virtual-env $(call split_string,$(shell poetry env list --full-path)) \
		.
