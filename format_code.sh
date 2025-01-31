#!/bin/bash

# Format code with black
echo "Running black..."
black mylocal tests

# Sort imports with isort
echo "Running isort..."
isort mylocal tests

# Lint code with flake8
echo "Running flake8..."
flake8 mylocal tests

echo "Code formatting and linting complete." 