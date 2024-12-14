# Variables
DOCKER_COMPOSE_FILE = docker-compose.yml
PYTHON_MAIN = src/main.py
TEST_DIR = tests
DOCKER_PYTHON_APP = python_app_container

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build            Build the Docker containers"
	@echo "  make up               Start the Docker containers"
	@echo "  make down             Stop and remove the Docker containers"
	@echo "  make logs             View logs from the Docker containers"
	@echo "  make tests            Run tests locally"
	@echo "  make run-local        Run the main application locally"
	@echo "  make run-docker       Run the main application in Docker"
	@echo "  make clean            Remove all Docker containers and volumes"

# Build Docker containers
.PHONY: build
build:
	docker-compose -f $(DOCKER_COMPOSE_FILE) build

# Start Docker containers
.PHONY: up
up:
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d

# Stop Docker containers
.PHONY: down
down:
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

# View logs
.PHONY: logs
logs:
	docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f

# Run tests locally
.PHONY: tests
tests:
	python -m unittest discover $(TEST_DIR)

# Run the main application locally
.PHONY: run-local
run-local:
	python $(PYTHON_MAIN)

# Run the main application in Docker
.PHONY: run-docker
run-docker:
	docker exec $(DOCKER_PYTHON_APP) python $(PYTHON_MAIN)

# Clean up Docker containers and volumes
.PHONY: clean
clean:
	docker-compose -f $(DOCKER_COMPOSE_FILE) down --volumes --remove-orphans
