## MyLocal 1.0 APIs

### Swagger API
https://app.swaggerhub.com/apis-docs/LAKINDUOSHADHA98_1/mylocal-service_backend_for_mylocal/1.0.0#/

### REST API

1. Get entity by id

[Entity Types](https://github.com/LDFLK/mylocal/blob/main/src/constants/EntityConstants.js)

https://service.mylocal.datafoundation.lk/my-local/my-local-service/v1.0/entities/LK-1

```json
{
  "LK-1": {
    "id": "LK-1",
    "name": "Western",
    "country_id": "LK",
    "province_id": "LK-1",
    "area": 3709,
    "population": 5850745,
    "province_capital": "Colombo",
    "fips": "CE36",
    "subs": [
      "EC-01",
      "EC-02",
      "EC-03",
      "LK-11",
      "LK-12",
      "LK-13"
    ],
    "supers": [],
    "eqs": [],
    "ints": [],
    "centroid": [6.83475266513655, 80.066990980517],
    "centroid_altitude": 65
  }
}
```

2. Census data by region based on Census Category

[Census Category](https://github.com/LDFLK/mylocal/blob/main/src/constants/CensusConstants.js)

https://service.mylocal.datafoundation.lk/my-local/my-local-service/v1.0/census/population-gender.regions.2012/LK-1

```json
{
  "LK-1": {
    "entity_id": "LK-1",
    "total_population": 5851130,
    "male": 2848649,
    "female": 3002481
  }
}
```

3. Get Region by Longitude and Latitude

https://service.mylocal.datafoundation.lk/my-local/my-local-service/v1.0/regions/6.053519,80.220978

```json
{
  "province": "LK-3",
  "district": "LK-31",
  "dsd": "LK-3139",
  "gnd": "LK-3139095"
}
```

4. Get Boundaries of a Region by Entity ID

https://service.mylocal.datafoundation.lk/my-local/my-local-service/v1.0/entity/coordinates/LK-1

```json
{
  "coordinates": [
    [
      [
        [79.8478155223685, 6.95682019354393],
        [79.8471083908276, 6.95525322658185],
        [79.8468726803139, 6.95525322658185],
        [79.8475798118548, 6.95642845180341],
        [79.8482869433957, 6.95760367702497],
        [79.8489940749366, 6.95838716050601],
        [79.8497012064775, 6.95917064398705],
        [79.8499369169912, 6.95995412746809],
        [79.8501726275048, 6.95995412746809],
        [79.8501726275048, 6.96034586920861],
        [79.8504083380184, 6.96034586920861],
        [79.8506440485321, 6.96034586920861],
        [79.8508797590457, 6.96073761094913],
        [79.851351180073, 6.96073761094913],
        [79.851351180073, 6.96112935268965],
        [79.851351180073, 6.96073761094913],
        [79.8511154695593, 6.96073761094913],
        [79.8506440485321, 6.96034586920861],
        [79.8504083380184, 6.96034586920861],
        [79.8501726275048, 6.95995412746809],
        [79.8492297854503, 6.95838716050601],
        [79.8485226539094, 6.95760367702497],
        [79.8478155223685, 6.95682019354393]
      ],
      [
        [80.187238662, 7.26237875114925],
        [80.1881815040545, 7.26355397637081],
        [80.1886529250818, 7.26394571811133],
        [80.1888886355954, 7.26394571811133],
        [80.1898314776499, 7.26394571811133],
        [80.1905386091908, 7.26355397637081],
        [80.1910100302181, 7.26316223463029],
        [80.1919528722726, 7.26198700940873],
        [80.1931314248408, 7.26081178418717],
        [80.1945456879226, 7.25963655896561],
        [80.1954885299771, 7.25885307548457],
        [80.1957242404908, 7.25846133374405],
        [80.1959599510044, 7.25846133374405]
      ]
    ]
  ],
  "type": "MultiPolygon"
}
```