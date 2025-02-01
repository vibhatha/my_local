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

## Querying the Database

To query the database, run:

```bash
python -m mylocal.query_mylocal --query "Your query here" --k 2
```

Example:

```bash
python -m mylocal.query_mylocal --query "What are the districts governed by the Western province?" --k 2
/Users/vibhatha/github/my_local/mylocal/ai/chat.py:35: LangChainDeprecationWarning: The method `Chain.run` was deprecated in langchain 0.1.0 and will be removed in 1.0. Use :meth:`~invoke` instead.
  return self.chain.run(question)


> Entering new GraphCypherQAChain chain...
Generated Cypher:
MATCH (d:District)-[:GOVERNED_BY]->(:Province {name: "Western"})
RETURN d.name
Full Context:
[{'d.name': 'Colombo'}, {'d.name': 'Gampaha'}, {'d.name': 'Kalutara'}]

> Finished chain.
Query Results:
C
o
l
o
m
b
o
,
 
G
a
m
p
a
h
a
,
 
K
a
l
u
t
a
r
a
```