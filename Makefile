.PHONY: help build test clean push run-spatial run-list run-all run-nrrd

# Docker image configuration
IMAGE_NAME = ghcr.io/m2aia/m2converter
TAG = latest
FULL_IMAGE = $(IMAGE_NAME):$(TAG)

# Directories
INPUT_DIR = kidney_glomerulie
OUTPUT_DIR = output
TEST_FILE = 01.imzML

# Default centroids for testing
TEST_CENTROIDS = 500.0 600.0 700.0

help:
	@echo "Available targets:"
	@echo "  build          - Build the Docker image"
	@echo "  test           - Run a quick test with spatial output"
	@echo "  test-all       - Test with all output formats"
	@echo "  test-no-centroids - Test with spatial output, no centroids (uses file's centroids)"
	@echo "  test-all-no-centroids - Test all output formats, no centroids (uses file's centroids)"
	@echo "  clean          - Remove output files"
	@echo "  push           - Push image to GitHub Container Registry"
	@echo "  run-spatial    - Process with spatial numpy output"
	@echo "  run-list       - Process with list numpy output"
	@echo "  run-all        - Process with all numpy outputs"
	@echo "  run-nrrd       - Process with NRRD output"
	@echo "  shell          - Open shell in container"

build:
	@echo "Building Docker image: $(FULL_IMAGE)"
	docker build -t $(FULL_IMAGE) .

test: build
	@echo "Running test with spatial output..."
	docker run --rm \
		-v $(PWD)/$(INPUT_DIR):/input:ro \
		-v $(PWD)/$(OUTPUT_DIR):/output \
		$(FULL_IMAGE) /input/$(TEST_FILE) \
		--output-dir /output \
		--centroids $(TEST_CENTROIDS) \
		--save-npy-spatial

test-all: build
	@echo "Running test with all output formats..."
	docker run --rm \
		-v $(PWD)/$(INPUT_DIR):/input:ro \
		-v $(PWD)/$(OUTPUT_DIR):/output \
		$(FULL_IMAGE) /input/$(TEST_FILE) \
		--output-dir /output \
		--centroids $(TEST_CENTROIDS) \
		--save-npy-spatial --save-npy-list --save-nrrd

test-no-centroids: build
	@echo "Running test with spatial output (no centroids - using file's centroids)..."
	docker run --rm \
		-v $(PWD)/$(INPUT_DIR):/input:ro \
		-v $(PWD)/$(OUTPUT_DIR):/output \
		$(FULL_IMAGE) /input/$(TEST_FILE) \
		--output-dir /output \
		--save-npy-spatial

test-all-no-centroids: build
	@echo "Running test with all output formats (no centroids - using file's centroids)..."
	docker run --rm \
		-v $(PWD)/$(INPUT_DIR):/input:ro \
		-v $(PWD)/$(OUTPUT_DIR):/output \
		$(FULL_IMAGE) /input/$(TEST_FILE) \
		--output-dir /output \
		--save-npy-spatial --save-npy-list --save-nrrd

run-spatial: build
	@echo "Processing $(TEST_FILE) with spatial output..."
	docker run --rm \
		-v $(PWD)/$(INPUT_DIR):/input:ro \
		-v $(PWD)/$(OUTPUT_DIR):/output \
		$(FULL_IMAGE) /input/$(TEST_FILE) \
		--output-dir /output \
		--save-npy-spatial

run-list: build
	@echo "Processing $(TEST_FILE) with list output..."
	docker run --rm \
		-v $(PWD)/$(INPUT_DIR):/input:ro \
		-v $(PWD)/$(OUTPUT_DIR):/output \
		$(FULL_IMAGE) /input/$(TEST_FILE) \
		--output-dir /output \
		--save-npy-list

run-all: build
	@echo "Processing $(TEST_FILE) with all outputs..."
	docker run --rm \
		-v $(PWD)/$(INPUT_DIR):/input:ro \
		-v $(PWD)/$(OUTPUT_DIR):/output \
		$(FULL_IMAGE) /input/$(TEST_FILE) \
		--output-dir /output \
		--save-npy-spatial --save-npy-list

run-nrrd: build
	@echo "Processing $(TEST_FILE) with NRRD output..."
	docker run --rm \
		-v $(PWD)/$(INPUT_DIR):/input:ro \
		-v $(PWD)/$(OUTPUT_DIR):/output \
		$(FULL_IMAGE) /input/$(TEST_FILE) \
		--output-dir /output \
		--centroids $(TEST_CENTROIDS) \
		--save-nrrd

clean:
	@echo "Cleaning output directory..."
	rm -rf $(OUTPUT_DIR)/*

push: build
	@echo "Pushing $(FULL_IMAGE) to registry..."
	docker push $(FULL_IMAGE)

shell:
	@echo "Opening shell in container..."
	docker run --rm -it \
		-v $(PWD)/$(INPUT_DIR):/input:ro \
		-v $(PWD)/$(OUTPUT_DIR):/output \
		$(FULL_IMAGE) /bin/bash
