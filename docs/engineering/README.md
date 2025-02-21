# Engineering

This section contains information about the engineering practices and processes used in the project.

## Table of Contents

- [API Policies](#api-policies)
- [GraphQL API](#graphql-api)
- [REST API](#rest-api)
- [Django Admin](#django-admin)
- [Testing](#testing)
- [Deployment](#deployment)

## API Policies

We have decided to not expose the internal APIs for data writing to the public via swagger or GraphQL. 
We will be using the Django command line to import the data.

All read APIs are exposed via GraphQL or REST. 

## GraphQL API

### GraphQL Schema

The GraphQL schema is defined in the `mylocalstats/population_stats/graphql/schema.py` file.

### GraphQL Queries

The GraphQL queries are defined in the `mylocalstats/population_stats/graphql/queries.py` file.

### GraphQL Mutations

The GraphQL mutations are defined in the `mylocalstats/population_stats/graphql/mutations.py` file.

### GraphQL Types

The GraphQL types are defined in the `mylocalstats/population_stats/graphql/types.py` file.

