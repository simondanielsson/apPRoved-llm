.PHONY:
	install_poetry
	install
	install_dev
	run
	build-image

IMAGE_NAME := approved-llm
IMAGE_TAG := latest

install_poetry:
	pip install --upgrade pip
	# Installing poetry if not installed...
	@python -m poetry --version || \
		pip install poetry

install: install_poetry
	poetry install

install_dev: install_poetry
	poetry install --with dev,test
	# Installs the pre-commit hook.
	pre-commit install

run:
	python -m src.main

build-image:
	echo "Building ${IMAGE_NAME}:${IMAGE_TAG} image...";
	docker image build -t ${IMAGE_NAME}:${IMAGE_TAG} .;
	echo "Image ${IMAGE_NAME}:${IMAGE_TAG} built.";
