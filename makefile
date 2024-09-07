# Define variables for directories and files
src.python := $(shell find ./src/churn_prediction_pipeline  -name "*.py")

dist.dir := dist

version := 1.0.0

# Default target
default: dist


# Install dependencies and set up the environment (assumes pip)
install:
	@echo "Installing dependencies..."
	pip install -r src/requirements.txt




# Create distribution tarballs and wheels
dist:
	@echo "Creating distribution files..."
	python setup.py sdist
	@echo "Distribution files created."

# Clean up build artifacts
clean:
	if exist $(dist.dir) rmdir /S /Q $(dist.dir)

	
