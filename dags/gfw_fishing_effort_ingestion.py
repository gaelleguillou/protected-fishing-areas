from datetime import datetime
import pandas as pd
import os
from sqlalchemy import create_engine
from airflow import DAG
from airflow.operators.python import PythonOperator

from config import Config

RAW_DATA_FOLDER = Config.RAW_DATA_FOLDER
PROCESSED_DATA_PATH = Config.PROCESSED_DATA_PATH
POSTGRES_CONN = Config.POSTGRES_CONN
TABLE_NAME = Config.TABLE_NAME
SRID = Config.SRID
CELL_SIZE_DEG = Config.CELL_SIZE_DEG
CHUNK_SIZE = 50_000  # Traite 50k lignes à la fois


def download_gfw_data(**kwargs):
    """
    Version minimale : les fichiers sont déjà présents localement dans data/raw
    Existe comme placeholder pour API.
    """
    print(f"📂 Recherche dans : {RAW_DATA_FOLDER}")

    if not os.path.exists(RAW_DATA_FOLDER):
        raise FileNotFoundError(f"❌ Le dossier {RAW_DATA_FOLDER} n'existe pas")

    files = [f for f in os.listdir(RAW_DATA_FOLDER) if f.endswith(".csv")]
    print(f"✅ Trouvé {len(files)} fichiers CSV dans {RAW_DATA_FOLDER}")

    # Estimation du nombre total de lignes (optionnel, pour info)
    total_estimated = 0
    for file in files[:3]:  # Juste les 3 premiers pour estimer
        file_path = os.path.join(RAW_DATA_FOLDER, file)
        with open(file_path) as f:
            line_count = sum(1 for _ in f) - 1  # -1 pour le header
            total_estimated += line_count

    avg_per_file = total_estimated / min(3, len(files))
    estimated_total = int(avg_per_file * len(files))
    print(f"📊 Estimation: ~{estimated_total:,} lignes au total")

    return len(files)


def load_raw_to_postgis(**kwargs):
    """
    Charge directement depuis CSV vers PostGIS par chunks
    Évite de saturer la RAM en traitant par morceaux
    """
    engine = create_engine(POSTGRES_CONN)
    csv_files = [f for f in os.listdir(RAW_DATA_FOLDER) if f.endswith(".csv")]

    first_chunk = True
    for file in csv_files:
        file_path = os.path.join(RAW_DATA_FOLDER, file)

        for chunk_df in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
            if_exists = "replace" if first_chunk else "append"

            chunk_df.to_sql(
                name="stg_gfw_fishing",
                con=engine,
                if_exists=if_exists,
                index=False,
                chunksize=10_000,
            )
            first_chunk = False

    print(f"\n🎉 Chargement terminé dans la table '{TABLE_NAME}'")


with DAG(
    dag_id="gfw_fishing_effort_ingestion",
    start_date=datetime(2026, 1, 25),
    schedule_interval="@monthly",
    catchup=False,
    tags=["protected-fishing-areas", "gfw", "fishing"],
) as dag:

    task_download = PythonOperator(
        task_id="download_gfw_data",
        python_callable=download_gfw_data,
    )

    task_load = PythonOperator(
        task_id="load_postgis_chunked",
        python_callable=load_raw_to_postgis,
    )

    task_download >> task_load
