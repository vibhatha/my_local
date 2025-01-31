# mylocal

A Python library for mylocal.

## Installation

### Setting up the Environment

1. **Create a Mamba Environment**: Create a new environment with Python 3.9:

   ```bash
   mamba create -n mylocal_env python=3.9
   ```

2. **Activate the Environment**: Activate the newly created environment:

   ```bash
   mamba activate mylocal_env
   ```

3. **Install Dependencies**: Once the environment is activated, install the project dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

## Usage

## Development Setup

To install development dependencies for code formatting and linting, run:

```bash
pip install -e ".[dev]"
```

To format and lint the code, use the provided script:

```bash
./format_code.sh
```
