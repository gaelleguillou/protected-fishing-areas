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
    RAW_DATA_FOLDER = os.path.join(
        BASE_PATH, "data/raw/fleet-monthly-csvs-10-v3-2024"
    )  # noqa E501
    PROCESSED_DATA_PATH = os.path.join(
        BASE_PATH, "data/processed/gfw_fleet_2024.parquet"
    )

    # Database
    POSTGRES_CONN = f"postgresql://pfa:pfa@{POSTGRES_HOST}:{POSTGRES_PORT}/pfa"
    TABLE_NAME = "fishing_effort_raw"

    # Geo
    SRID = 4326
    CELL_SIZE_DEG = 0.1
