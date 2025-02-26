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

    # Define the hierarchy of governing bodies
    # Format: governing_type: {
    #     'parents': [(parent_type, parent_id_column)],
    #     'children': [child_type]
    # }
    hierarchy = {
        "Country": {
            "parents": [],
            "children": ["Province"]
        },
        "Province": {
            "parents": [("Country", "country_id")],
            "children": ["ED", "District"]
        },
        "District": {
            "parents": [("Province", "province_id")],
            "children": ["PD", "LG", "MOH", "DSD"]
        },
        "PD": {
            "parents": [("DSD", "dsd_id")], # not sure about this
            "children": ["GND"]
        },
        "DSD": {
            "parents": [
                ("LG", "lg_id"),
                ("MOH", "moh_id"),
                ("District", "district_id")
            ],
            "children": ["PD"]
        },
        "ED": {
            "parents": [("District", "district_id")],
            "children": ["PD", "LG", "DSD"]
        },
        "GND": {
            "parents": [("PD", "pd_id")],
            "children": []
        },
        "LG": {
            "parents": [
                ("District", "district_id"),
                ("ED", "ed_id")
            ],
            "children": ["GND"]
        },
        "MOH": {
            "parents": [
                ("District", "district_id"),
                ("ED", "ed_id")
            ],
            "children": ["DSD"]
        }
    }

    # Define processing order (important for creating parents before children)
    processing_steps = [
        ("country", "Country"),
        ("province", "Province"),
        ("district", "District"),
        ("ed", "ElectoralDivision"),
        ("moh", "MedicalOfficerOfHealth"),
        ("lg", "LocalGovernment"),
        ("dsd", "DSD"),
        ("pd", "PollingDivision"),
        ("gnd", "GramaNiladhari"),
    ]

    # Process all files using context managers
    with ConnectorManager() as manager:
        with Neo4jDriver(uri, username, password) as driver:
            manager.register_connector("neo4j", driver)

            # Process all files
            for file_key, governing_type in processing_steps:
                # Get all parent relationships for this type
                parent_relationships = hierarchy[governing_type]["parents"]
                for parent_type, parent_key in parent_relationships:
                    driver.process_file(
                        file_paths[file_key],
                        governing_type,
                        parent_key
                    )


if __name__ == "__main__":
    print("Ingesting data...")
    disabled = True
    if not disabled:
        ingest_data()
    else:
        print("Ingestion disabled")
