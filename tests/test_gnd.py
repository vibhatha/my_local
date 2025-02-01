import os
from pathlib import Path
import csv
from collections import defaultdict

import pytest

from mylocal.db.neo4j_driver import Neo4jDriver


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


def test_gnd_counts_match_neo4j(neo4j_driver):
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
