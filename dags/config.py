import os


class Config:
    IS_DOCKER = (
        os.path.exists("/.dockerenv")
        or os.environ.get("AIRFLOW_HOME") is not None  # noqa E501
    )

    if IS_DOCKER:
        BASE_PATH = "/opt/airflow"
        POSTGRES_HOST = "postgres-data"
        POSTGRES_PORT = 5432
    else:
        BASE_PATH = "."
        POSTGRES_HOST = "localhost"
        POSTGRES_PORT = 5433

    # Chemins
    GFW_RAW_DATA_FOLDER = os.path.join(BASE_PATH, "data/raw/gfw")  # noqa E501
    WDPA_RAW_DATA_FOLDER = os.path.join(BASE_PATH, "data/raw/wdpa")  # noqa E501

    # Database
    POSTGRES_CONN = f"postgresql://pfa:pfa@{POSTGRES_HOST}:{POSTGRES_PORT}/pfa"
    GFW_TABLE_NAME = "fishing_effort_raw"
    WDPA_TABLE_NAME = "protected_areas_raw"

    # Geo
    SRID = 4326
    CELL_SIZE_DEG = 0.1
