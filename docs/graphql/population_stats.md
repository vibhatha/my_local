# GraphQL API Usage Guide

This guide provides comprehensive examples of how to use the MyLocalStats GraphQL API. All examples can be tested using the GraphiQL interface at `/graphql/`.

## Table of Contents
- [Basic Concepts](#basic-concepts)
- [Region Queries](#region-queries)
- [Population Statistics](#population-statistics)
- [Demographic Data](#demographic-data)
- [Advanced Queries](#advanced-queries)
- [Using Variables](#using-variables)

## Basic Concepts

The API provides access to Sri Lankan population statistics across different regional levels. Each query can be filtered by:
- Region type (province, district, etc.)
- Year (default: 2012)
- Region ID (e.g., "LK-1")

## Region Queries

### Get All Regions

```graphql
query {
    regions {
        entityId
        name
        type
    }
}
```

### Get Regions by Type

```graphql
query {
    regions(type: "province") {
        entityId
        name
    }
}

```

### Get Single Region

```graphql
query {
  region(entityId: "LK-1") {
    name
    type
  }
}
```

## Population Statistics

### Total Population

#### Get All Population Data

```graphql
query {
  totalPopulations {
    region {
      name
      type
    }
    totalPopulation
    year
  }
}
```

#### Get Population by Region Type and Year

```graphql
query {
  totalPopulations(regionType: "province", year: 2012) {
    region {
      name
    }
    totalPopulation
  }
}
```

### Gender Distribution

#### Get Gender Statistics for a Region

```graphql
query {
  genderDistribution(regionId: "LK-1") {
    region {
      name
    }
    totalPopulation
    male
    female
    year
  }
}
```

## Demographic Data

### Age Distribution

#### Get Age Groups for a Region
```graphql
query {
  ageDistribution(regionId: "LK-1") {
    region {
      name
    }
    totalPopulation
    lessThan10
    age10To19
    age20To29
    age30To39
    age40To49
    age50To59
    age60To69
    age70To79
    age80To89
    age90AndAbove
    year
  }
}
```

### Ethnicity Distribution

#### Get Ethnicity Data

```graphql
query {
  ethnicityDistribution(regionId: "LK-1") {
    region {
      name
    }
    totalPopulation
    sinhalese
    slTamil
    indTamil
    slMoor
    burgher
    malay
    slChetty
    bharatha
    otherEth
    year
  }
}
```

### Religious Affiliation

#### Get Religious Data
```graphql
query {
  religiousAffiliation(regionId: "LK-1") {
    region {
      name
    }
    totalPopulation
    buddhist
    hindu
    islam
    romanCatholic
    otherChristian
    other
    year
  }
}
```

### Marital Status

#### Get Marital Status Data

```graphql
query {
  maritalStatus(regionId: "LK-1") {
    region {
      name
    }
    totalPopulation
    neverMarried
    marriedRegistered
    marriedCustomary
    separatedLegally
    separatedNonLegal
    divorced
    widowed
    notStated
    year
  }
}
```

## Advanced Queries

### Combined Data Query

```graphql
query {
  region(entityId: "LK-1") {
    name
    type
  }
  totalPopulation(regionId: "LK-1") {
    totalPopulation
    year
  }
  genderDistribution(regionId: "LK-1") {
    male
    female
  }
  religiousAffiliation(regionId: "LK-1") {
    buddhist
    hindu
    islam
  }
}
```

### Regional Overview

```graphql
query {
  regions(type: "province") {
    entityId
    name
  }
  totalPopulations(regionType: "province") {
    region {
      name
    }
    totalPopulation
  }
  genderDistributions(regionType: "province") {
    region {
      name
    }
    male
    female
  }
  ageDistributions(regionType: "province") {
    region {
      name
    }
    lessThan10
    age20To29
    age60To69
  }
}
```

## Using Variables

Variables allow you to make dynamic queries. Here's an example:

```graphql
query GetRegionData($regionId: String!, $regionType: String) {
  region(entityId: $regionId) {
    name
    type
  }
  religiousAffiliations(regionType: $regionType) {
    region {
      name
    }
    totalPopulation
  }
}
```

Variables JSON:
```json
{
  "regionId": "LK-1",
  "regionType": "province"
}
```

# Using variables for flexibility

```graphql
query GetProvinceReligion($regionId: String!) {
  religiousAffiliation(regionId: $regionId) {
    region {
      name
      type
    }
    totalPopulation
    buddhist
    hindu
    islam
    romanCatholic
    otherChristian
    other
    year
  }
}
```

### Variables

```json
{
  "regionId": "LK-1"  # Western Province
}
```

## Available Options

### Region Types
- province
- district
- dsd
- gnd
- ed
- lg
- pd
- moh
- country

### Years Available
- 2012 (default)

## Error Handling

All queries include proper error handling. Common errors:
- Region not found
- Invalid region type
- Data not available for specified year

## Best Practices

1. Always specify only the fields you need
2. Use variables for dynamic queries
3. Consider pagination for large data sets
4. Include error handling in your applications

## Need Help?

For additional support:
- Use the GraphiQL interface at `/graphql/`
- Check the API documentation at `/swagger/`
- Contact the development team