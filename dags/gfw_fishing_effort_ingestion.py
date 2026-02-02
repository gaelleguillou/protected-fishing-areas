from datetime import datetime
import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from config import Config

GFW_RAW_DATA_FOLDER = Config.GFW_RAW_DATA_FOLDER
POSTGRES_CONN = Config.POSTGRES_CONN
GFW_TABLE_NAME = Config.GFW_TABLE_NAME
SRID = Config.SRID
CELL_SIZE_DEG = Config.CELL_SIZE_DEG
CHUNK_SIZE = 50_000  # Traite 50k lignes à la fois


def download_gfw_data(**kwargs):
    """
    Version minimale : les fichiers sont déjà présents localement dans data/raw
    Existe comme placeholder pour API.
    """
    print(f"📂 Recherche dans : {GFW_RAW_DATA_FOLDER}")

    if not os.path.exists(GFW_RAW_DATA_FOLDER):
        raise FileNotFoundError(
            f"❌ Le dossier {GFW_RAW_DATA_FOLDER} n'existe pas"
        )  # noqa E501

    files = [
        f for f in os.listdir(GFW_RAW_DATA_FOLDER) if f.endswith(".csv")
    ]  # noqa E501
    print(f"✅ Trouvé {len(files)} fichiers CSV dans {GFW_RAW_DATA_FOLDER}")

    # Estimation du nombre total de lignes (optionnel, pour info)
    total_estimated = 0
    for file in files[:3]:  # Juste les 3 premiers pour estimer
        file_path = os.path.join(GFW_RAW_DATA_FOLDER, file)
        with open(file_path) as f:
            line_count = sum(1 for _ in f) - 1  # -1 pour le header
            total_estimated += line_count

    avg_per_file = total_estimated / min(3, len(files))
    estimated_total = int(avg_per_file * len(files))
    print(f"📊 Estimation: ~{estimated_total:,} lignes au total")

    return len(files)


def load_raw_to_postgis(**kwargs):
    hook = PostgresHook(postgres_conn_id="pfa_postgis")
    conn = hook.get_conn()
    cursor = conn.cursor()

    # 1. Définition de la structure GFW (ajustée aux colonnes standards GFW)
    # On reste en TEXT pour le chargement RAW afin d'éviter les erreurs de cast
    create_table_sql = """
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE TABLE IF NOT EXISTS raw.stg_gfw_fishing (
        mmsi TEXT,
        timestamp TEXT,
        lat TEXT,
        lon TEXT,
        speed TEXT,
        course TEXT,
        is_fishing TEXT,
        source TEXT,
        vessel_class TEXT,
        flag TEXT
    );
    TRUNCATE TABLE raw.stg_gfw_fishing;
    """

    # Lister les fichiers dans le dossier GFW
    csv_files = [
        f for f in os.listdir(GFW_RAW_DATA_FOLDER) if f.endswith(".csv")
    ]  # noqa E501

    try:
        print("Initialisation de la table raw.stg_gfw_fishing...")
        cursor.execute(create_table_sql)

        for file in csv_files:
            file_path = os.path.join(GFW_RAW_DATA_FOLDER, file)
            print(f"🚀 Chargement ultra-rapide de {file} via COPY...")

            with open(file_path, "r", encoding="utf-8") as f:
                # copy_expert est environ 10x à 100x + rapide que pandas.to_sql
                cursor.copy_expert(
                    sql="COPY raw.stg_gfw_fishing FROM STDIN WITH (FORMAT CSV, HEADER)",  # noqa E501
                    file=f,
                )

        conn.commit()
        print(f"✅ Chargement terminé : {len(csv_files)} fichiers importés.")

    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors du chargement GFW : {e}")
        raise
    finally:
        cursor.close()
        conn.close()


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

    run_dbt = BashOperator(
        task_id="run_dbt_transformations",
        bash_command="cd /opt/airflow/dbt/protected_fishing_areas && dbt run --profiles-dir .",  # noqa E501
    )

    task_download >> task_load >> run_dbt
