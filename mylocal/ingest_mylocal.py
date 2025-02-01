import os

from mylocal.db.connect import ConnectorManager
from mylocal.db.neo4j_driver import Neo4jDriver


def ingest_data():
    # Get Neo4j connection details from environment variables
    uri = os.getenv("NEO4J_MYLOCAL_DB_URI")
    username = os.getenv("NEO4J_MYLOCAL_USERNAME")
    password = os.getenv("NEO4J_MYLOCAL_PASSWORD")
    # Base directory for data files
    base_dir = os.getenv("MYLOCAL_DATA_DIR", "/mnt/data")

    if not all([uri, username, password, base_dir]):
        raise ValueError("Missing required Neo4j environment variables")

    # File paths
    file_paths = {
        "country": os.path.join(base_dir, "country.tsv"),
        "province": os.path.join(base_dir, "province.tsv"),
        "district": os.path.join(base_dir, "district.tsv"),
        "dsd": os.path.join(base_dir, "dsd.tsv"),
        "ed": os.path.join(base_dir, "ed.tsv"),
        "gnd": os.path.join(base_dir, "gnd.tsv"),
        "lg": os.path.join(base_dir, "lg.tsv"),
        "moh": os.path.join(base_dir, "moh.tsv"),
        "pd": os.path.join(base_dir, "pd.tsv"),
    }

    # Define processing steps
    processing_steps = [
        ("country", "Country", None, None),
        ("province", "Province", "country_id", "Country"),
        ("district", "District", "province_id", "Province"),
        ("dsd", "DSD", "district_id", "District"),
        ("ed", "ED", "province_id", "Province"),
        ("gnd", "Locale", "dsd_id", "DSD"),
        ("moh", "MOH", "district_id", "District"),
        ("lg", "Local", "district_id", "District"),
        ("pd", "PD", "ed_id", "ED"),
    ]

    # Process all files using context managers
    with ConnectorManager() as manager:
        with Neo4jDriver(uri, username, password) as driver:
            manager.register_connector("neo4j", driver)

            # Process all files
            for file_key, node_label, parent_key, parent_label in processing_steps:
                driver.process_file(file_paths[file_key], node_label, parent_key, parent_label)


if __name__ == "__main__":
    print("Ingesting data...")
    disabled = True
    if not disabled:
        ingest_data()
    else:
        print("Ingestion disabled")
