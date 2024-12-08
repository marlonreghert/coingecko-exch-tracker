# Variables
PYTHONPATH=src
TEST_CMD=python -m unittest discover -s tests -p "test_*.py"
RUN_CMD=python -m src.table_updater
DOCKER_IMAGE=exchtracker
DOCKER_CONTAINER=exchtracker_container

# Run tests locally
test:
	PYTHONPATH=$(PYTHONPATH) $(TEST_CMD)

# Run the application locally
run:
	PYTHONPATH=$(PYTHONPATH) $(RUN_CMD)

# Build Docker image
docker-build:
	docker build -t $(DOCKER_IMAGE) .

# Run Docker container
docker-run:
	docker run --name $(DOCKER_CONTAINER) -v $(PWD)/data:/data -d $(DOCKER_IMAGE)

# Enter the Docker container
docker-shell:
	docker exec -it $(DOCKER_CONTAINER) /bin/bash

# View /data/processed folder inside the Docker container
view-processed:
	docker exec -it $(DOCKER_CONTAINER) ls /data/processed

# Stop and remove the Docker container
docker-clean:
	docker stop $(DOCKER_CONTAINER) && docker rm $(DOCKER_CONTAINER)
