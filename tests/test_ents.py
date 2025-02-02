import os
from pathlib import Path
import csv
from collections import defaultdict

import pytest

from mylocal.db.neo4j_driver import Neo4jDriver

"""
TESTCASES
==========

Simple Queries
--------------

1. Districts in Provinces [DONE]
2. GNDs in Districts [DONE]
3. GNDs in Provinces [DONE]
4. DSDs in Districts [DONE]
5. DSDs in Provinces [DONE]
6. DSDs in EDs [DONE]
7. EDs in Province [DONE]
8. LGs in Districts [DONE]
9. LGs in Province [DONE]
10. MOH in District [DONE]
11. PD in ED [DONE]


Complex Queries (TODO)
----------------------

1. DSDs and EDs that share the same province [DONE]
...

"""


def ent_dir():
    return Path(__file__).parent.parent / "external" / "gig-data" / "ents"


def gnd_path():
    return ent_dir() / "gnd.tsv"


def country_path():
    return ent_dir() / "country.tsv"


def district_path():
    return ent_dir() / "district.tsv"


def dsd_path():
    return ent_dir() / "dsd.tsv"


def ed_path():
    return ent_dir() / "ed.tsv"


def lg_path():
    return ent_dir() / "lg.tsv"


def moh_path():
    return ent_dir() / "moh.tsv"


def pd_path():
    return ent_dir() / "pd.tsv"


def pd_with_postal_path():
    return ent_dir() / "pd_with_postal.tsv"


def province_path():
    return ent_dir() / "province.tsv"


def test_data_paths():
    assert gnd_path().exists()


@pytest.fixture(scope="session")
def neo4j_driver():
    uri = os.getenv("NEO4J_MYLOCAL_DB_URI")
    username = os.getenv("NEO4J_MYLOCAL_USERNAME")
    password = os.getenv("NEO4J_MYLOCAL_PASSWORD")
    driver = Neo4jDriver(uri=uri, user=username, password=password)
    yield driver
    # Cleanup after all tests are done
    driver.close()


def test_gnd_locale_count_for_western_province(neo4j_driver):
    query = """
    MATCH (l:Locale)-[:GOVERNED_BY]->(dsd:DSD)-[:GOVERNED_BY]->(d:District)-[:GOVERNED_BY]->
    (p:Province {name: "Western"})
    RETURN COUNT(l) AS localeCount
    """
    result = neo4j_driver.execute_query(query)
    assert result[0]["localeCount"] == 2496


def load_province_map():
    province_name_map = {}
    with open(province_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            province_name_map[row['id']] = row['name']
    return province_name_map


def count_gnds_per_province():
    gnd_count_per_province = defaultdict(int)
    with open(gnd_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            province_id = row['province_id']
            gnd_count_per_province[province_id] += 1
    return gnd_count_per_province


def test_gnd_for_province(neo4j_driver):
    # Get counts from TSV files
    province_map = load_province_map()
    tsv_gnd_counts = count_gnds_per_province()
    
    # Query Neo4j for GND counts per province
    query = """
    MATCH (l:Locale)-[:GOVERNED_BY*]->(p:Province)
    WITH p.id as province_id, p.name as province_name, COUNT(l) as gnd_count
    RETURN province_id, province_name, gnd_count
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare counts
    for result in neo4j_results:
        province_id = result['province_id']
        neo4j_count = result['gnd_count']
        tsv_count = tsv_gnd_counts[province_id]
        province_name = province_map[province_id]
        print(f"Province: {province_name} (ID: {province_id}) - Neo4j count: {neo4j_count}, TSV count: {tsv_count}")
        
        assert neo4j_count == tsv_count, (
            f"Mismatch for province {province_name} (ID: {province_id}): "
            f"Neo4j count: {neo4j_count}, TSV count: {tsv_count}"
        )


def load_district_map():
    district_name_map = {}
    with open(district_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            district_name_map[row['id']] = row['name']
    return district_name_map


def get_districts_per_province():
    districts_per_province = defaultdict(set)
    with open(district_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            province_id = row['province_id']
            district_id = row['id']
            districts_per_province[province_id].add(district_id)
    return districts_per_province


def test_district_for_province(neo4j_driver):
    # Get data from TSV files
    tsv_districts = get_districts_per_province()
    
    # Query Neo4j for districts per province
    query = """
    MATCH (d:District)-[:GOVERNED_BY]->(p:Province)
    WITH p.id as province_id, p.name as province_name, 
         collect({id: d.id, name: d.name}) as districts
    RETURN province_id, province_name, districts
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare results
    for result in neo4j_results:
        province_id = result['province_id']
        province_name = result['province_name']
        neo4j_district_ids = {d['id'] for d in result['districts']}
        tsv_district_ids = tsv_districts[province_id]
        
        # Print districts for each province
        neo4j_district_names = sorted([f"{d['name']} ({d['id']})" for d in result['districts']])
        print(f"Province: {province_name} (ID: {province_id}) - "
              f"Districts: {', '.join(neo4j_district_names)}")
        
        assert neo4j_district_ids == tsv_district_ids, (
            f"Mismatch for province {province_name} (ID: {province_id}): \n"
            f"Neo4j districts: {sorted(neo4j_district_ids)}\n"
            f"TSV districts: {sorted(tsv_district_ids)}"
        )


def get_dsds_per_district():
    dsds_per_district = defaultdict(set)
    with open(dsd_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            district_id = row['district_id']
            dsd_id = row['id']
            dsds_per_district[district_id].add(dsd_id)
    return dsds_per_district


def test_dsd_per_district(neo4j_driver):
    # Get data from TSV files
    tsv_dsds = get_dsds_per_district()
    
    # Query Neo4j for DSDs per district
    query = """
    MATCH (dsd:DSD)-[:GOVERNED_BY]->(d:District)
    WITH d.id as district_id, d.name as district_name, 
         collect({id: dsd.id, name: dsd.name}) as dsds
    RETURN district_id, district_name, dsds
    ORDER BY district_name
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare results
    for result in neo4j_results:
        district_id = result['district_id']
        district_name = result['district_name']
        neo4j_dsd_ids = {d['id'] for d in result['dsds']}
        tsv_dsd_ids = tsv_dsds[district_id]
        
        # Print DSDs for each district
        neo4j_dsd_names = sorted([f"{d['name']} ({d['id']})" for d in result['dsds']])
        print(f"District: {district_name} (ID: {district_id}) - "
              f"DSDs: {', '.join(neo4j_dsd_names)}")
        
        assert neo4j_dsd_ids == tsv_dsd_ids, (
            f"Mismatch for district {district_name} (ID: {district_id}): \n"
            f"Neo4j DSDs: {sorted(neo4j_dsd_ids)}\n"
            f"TSV DSDs: {sorted(tsv_dsd_ids)}"
        )


def get_eds_per_province():
    eds_per_province = defaultdict(set)
    with open(ed_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            province_id = row['province_id']
            ed_id = row['id']
            eds_per_province[province_id].add(ed_id)
    return eds_per_province


def test_ed_for_province(neo4j_driver):
    # Get data from TSV files
    tsv_eds = get_eds_per_province()
    
    # Query Neo4j for EDs per province
    query = """
    MATCH (ed:ED)-[:GOVERNED_BY]->(p:Province)
    WITH p.id as province_id, p.name as province_name, 
         collect({id: ed.id, name: ed.name}) as eds
    RETURN province_id, province_name, eds
    ORDER BY province_name
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare results
    for result in neo4j_results:
        province_id = result['province_id']
        province_name = result['province_name']
        neo4j_ed_ids = {d['id'] for d in result['eds']}
        tsv_ed_ids = tsv_eds[province_id]
        
        # Print EDs for each province
        neo4j_ed_names = sorted([f"{d['name']} ({d['id']})" for d in result['eds']])
        print(f"Province: {province_name} (ID: {province_id}) - "
              f"Electoral Districts: {', '.join(neo4j_ed_names)}")
        
        assert neo4j_ed_ids == tsv_ed_ids, (
            f"Mismatch for province {province_name} (ID: {province_id}): \n"
            f"Neo4j EDs: {sorted(neo4j_ed_ids)}\n"
            f"TSV EDs: {sorted(tsv_ed_ids)}"
        )


def get_lgs_per_district():
    lgs_per_district = defaultdict(set)
    with open(lg_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            district_id = row['district_id']
            lg_id = row['id']
            lgs_per_district[district_id].add(lg_id)
    return lgs_per_district


def test_lg_per_district(neo4j_driver):
    # Get data from TSV files
    tsv_lgs = get_lgs_per_district()
    
    # Query Neo4j for LGs per district
    query = """
    MATCH (lg:Local)-[:GOVERNED_BY]->(d:District)
    WITH d.id as district_id, d.name as district_name, 
         collect({id: lg.id, name: lg.name}) as lgs
    RETURN district_id, district_name, lgs
    ORDER BY district_name
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare results
    for result in neo4j_results:
        district_id = result['district_id']
        district_name = result['district_name']
        neo4j_lg_ids = {d['id'] for d in result['lgs']}
        tsv_lg_ids = tsv_lgs[district_id]
        
        # Print LGs for each district
        neo4j_lg_names = sorted([f"{d['name']} ({d['id']})" for d in result['lgs']])
        print(f"District: {district_name} (ID: {district_id}) - "
              f"Local Governments: {', '.join(neo4j_lg_names)}")
        
        assert neo4j_lg_ids == tsv_lg_ids, (
            f"Mismatch for district {district_name} (ID: {district_id}): \n"
            f"Neo4j LGs: {sorted(neo4j_lg_ids)}\n"
            f"TSV LGs: {sorted(tsv_lg_ids)}"
        )


def get_lgs_per_province():
    lgs_per_province = defaultdict(set)
    with open(lg_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            province_id = row['province_id']
            lg_id = row['id']
            lgs_per_province[province_id].add(lg_id)
    return lgs_per_province

def test_lg_for_province(neo4j_driver):
    # Get data from TSV files
    tsv_lgs = get_lgs_per_province()
    
    # Query Neo4j for LGs per province
    query = """
    MATCH (lg:Local)-[:GOVERNED_BY*]->(p:Province)
    WITH p.id as province_id, p.name as province_name, 
         collect({id: lg.id, name: lg.name}) as lgs
    RETURN province_id, province_name, lgs
    ORDER BY province_name
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare results
    for result in neo4j_results:
        province_id = result['province_id']
        province_name = result['province_name']
        neo4j_lg_ids = {d['id'] for d in result['lgs']}
        tsv_lg_ids = tsv_lgs[province_id]
        
        # Print LGs for each province
        neo4j_lg_names = sorted([f"{d['name']} ({d['id']})" for d in result['lgs']])
        print(f"Province: {province_name} (ID: {province_id}) - "
              f"Local Governments: {', '.join(neo4j_lg_names)}")
        
        assert neo4j_lg_ids == tsv_lg_ids, (
            f"Mismatch for province {province_name} (ID: {province_id}): \n"
            f"Neo4j LGs: {sorted(neo4j_lg_ids)}\n"
            f"TSV LGs: {sorted(tsv_lg_ids)}"
        )


def get_dsds_per_province():
    dsds_per_province = defaultdict(set)
    with open(dsd_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            province_id = row['province_id']
            dsd_id = row['id']
            dsds_per_province[province_id].add(dsd_id)
    return dsds_per_province


def test_dsd_for_province(neo4j_driver):
    # Get data from TSV files
    tsv_dsds = get_dsds_per_province()
    
    # Query Neo4j for DSDs per province
    query = """
    MATCH (dsd:DSD)-[:GOVERNED_BY*]->(p:Province)
    WITH p.id as province_id, p.name as province_name, 
         collect({id: dsd.id, name: dsd.name}) as dsds
    RETURN province_id, province_name, dsds
    ORDER BY province_name
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare results
    for result in neo4j_results:
        province_id = result['province_id']
        province_name = result['province_name']
        neo4j_dsd_ids = {d['id'] for d in result['dsds']}
        tsv_dsd_ids = tsv_dsds[province_id]
        
        # Print DSDs for each province
        neo4j_dsd_names = sorted([f"{d['name']} ({d['id']})" for d in result['dsds']])
        print(f"Province: {province_name} (ID: {province_id}) - "
              f"DSDs: {', '.join(neo4j_dsd_names)}")
        
        assert neo4j_dsd_ids == tsv_dsd_ids, (
            f"Mismatch for province {province_name} (ID: {province_id}): \n"
            f"Neo4j DSDs: {sorted(neo4j_dsd_ids)}\n"
            f"TSV DSDs: {sorted(tsv_dsd_ids)}"
        )


def get_dsds_and_eds_by_province():
    # Get DSDs per province
    dsds_per_province = defaultdict(set)
    with open(dsd_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            province_id = row['province_id']
            dsd_id = row['id']
            dsds_per_province[province_id].add(dsd_id)
    
    # Get EDs per province
    eds_per_province = defaultdict(set)
    with open(ed_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            province_id = row['province_id']
            ed_id = row['id']
            eds_per_province[province_id].add(ed_id)
            
    return dsds_per_province, eds_per_province


def test_dsd_per_ed(neo4j_driver):
    # Get data from TSV files
    dsds_per_province, eds_per_province = get_dsds_and_eds_by_province()
    
    # Query Neo4j for DSDs and EDs that share the same province
    query = """
    MATCH (dsd:DSD)-[:GOVERNED_BY*]->(p:Province)<-[:GOVERNED_BY]-(ed:ED)
    WITH p.id as province_id, p.name as province_name,
         ed.id as ed_id, ed.name as ed_name,
         collect({id: dsd.id, name: dsd.name}) as dsds
    RETURN province_id, province_name, ed_id, ed_name, dsds
    ORDER BY province_name, ed_name
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare results
    for result in neo4j_results:
        province_id = result['province_id']
        province_name = result['province_name']
        ed_id = result['ed_id']
        ed_name = result['ed_name']
        
        # Verify ED belongs to province
        assert ed_id in eds_per_province[province_id], (
            f"ED {ed_name} ({ed_id}) not found in province {province_name} ({province_id})"
        )
        
        # Get Neo4j DSDs for this ED's province
        neo4j_dsd_ids = {d['id'] for d in result['dsds']}
        
        # Get TSV DSDs for this province
        tsv_dsd_ids = dsds_per_province[province_id]
        
        # Print DSDs for each ED
        neo4j_dsd_names = sorted([f"{d['name']} ({d['id']})" for d in result['dsds']])
        print(f"Province: {province_name} (ID: {province_id}) - "
              f"ED: {ed_name} (ID: {ed_id}) - "
              f"DSDs: {', '.join(neo4j_dsd_names)}")
        
        assert neo4j_dsd_ids == tsv_dsd_ids, (
            f"Mismatch for ED {ed_name} (ID: {ed_id}) in province {province_name} (ID: {province_id}): \n"
            f"Neo4j DSDs: {sorted(neo4j_dsd_ids)}\n"
            f"TSV DSDs: {sorted(tsv_dsd_ids)}"
        )


def get_mohs_per_district():
    mohs_per_district = defaultdict(set)
    with open(moh_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            district_id = row['district_id']
            moh_id = row['id']
            mohs_per_district[district_id].add(moh_id)
    return mohs_per_district


def test_moh_per_district(neo4j_driver):
    # Get data from TSV files
    tsv_mohs = get_mohs_per_district()
    
    # Query Neo4j for MOHs per district
    query = """
    MATCH (moh:MOH)-[:GOVERNED_BY]->(d:District)
    WITH d.id as district_id, d.name as district_name, 
         collect({id: moh.id, name: moh.name}) as mohs
    RETURN district_id, district_name, mohs
    ORDER BY district_name
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare results
    for result in neo4j_results:
        district_id = result['district_id']
        district_name = result['district_name']
        neo4j_moh_ids = {d['id'] for d in result['mohs']}
        tsv_moh_ids = tsv_mohs[district_id]
        
        # Print MOHs for each district
        neo4j_moh_names = sorted([f"{d['name']} ({d['id']})" for d in result['mohs']])
        print(f"District: {district_name} (ID: {district_id}) - "
              f"MOH Areas: {', '.join(neo4j_moh_names)}")
        
        assert neo4j_moh_ids == tsv_moh_ids, (
            f"Mismatch for district {district_name} (ID: {district_id}): \n"
            f"Neo4j MOHs: {sorted(neo4j_moh_ids)}\n"
            f"TSV MOHs: {sorted(tsv_moh_ids)}"
        )


def get_pds_per_ed():
    pds_per_ed = defaultdict(set)
    with open(pd_path(), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            ed_id = row['ed_id']
            pd_id = row['id']
            pds_per_ed[ed_id].add(pd_id)
    return pds_per_ed


def test_pd_per_ed(neo4j_driver):
    # Get data from TSV files
    tsv_pds = get_pds_per_ed()
    
    # Query Neo4j for PDs per ED
    query = """
    MATCH (pd:PD)-[:GOVERNED_BY]->(ed:ED)
    WITH ed.id as ed_id, ed.name as ed_name, 
         collect({id: pd.id, name: pd.name}) as pds
    RETURN ed_id, ed_name, pds
    ORDER BY ed_name
    """
    neo4j_results = neo4j_driver.execute_query(query)
    
    # Compare results
    for result in neo4j_results:
        ed_id = result['ed_id']
        ed_name = result['ed_name']
        neo4j_pd_ids = {d['id'] for d in result['pds']}
        tsv_pd_ids = tsv_pds[ed_id]
        
        # Print PDs for each ED
        neo4j_pd_names = sorted([f"{d['name']} ({d['id']})" for d in result['pds']])
        print(f"Electoral District: {ed_name} (ID: {ed_id}) - "
              f"Polling Divisions: {', '.join(neo4j_pd_names)}")
        
        assert neo4j_pd_ids == tsv_pd_ids, (
            f"Mismatch for ED {ed_name} (ID: {ed_id}): \n"
            f"Neo4j PDs: {sorted(neo4j_pd_ids)}\n"
            f"TSV PDs: {sorted(tsv_pd_ids)}"
        )
