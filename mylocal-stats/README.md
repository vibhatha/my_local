# MyLocalStats

This is the README file for the MyLocalStats project.

# mylocalstats

A Django backend to manage data


## Create App

```bash
python manage.py startapp population_stats
```

## Installation

### Development Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Set up pre-commit hooks:
```bash
pre-commit install
```

## Development Tools

This project uses several development tools:

- **Black**: Code formatting (line length: 100)
- **isort**: Import sorting
- **flake8**: Code linting
- **autoflake**: Remove unused imports
- **yapf**: Additional code formatting
- **pre-commit**: Git hooks for code quality

## Creating New Apps

To create a new Django app:
```bash
python manage.py startapp app_name
```

## Testing

Run tests with:
```bash
pytest
```

## Dependencies

### Core Dependencies
- Django >= 4.0.0
- pandas >= 2.2.0
- psycopg2-binary >= 2.9.9

### Development Dependencies
- black >= 24.2.0
- isort >= 5.13.2
- flake8 >= 7.0.0
- pre-commit >= 3.6.0
- autopep8 >= 2.0.0
- autoflake >= 2.2.0
- yapf >= 0.40.0

## Python Compatibility

Requires Python 3.9 or higher.