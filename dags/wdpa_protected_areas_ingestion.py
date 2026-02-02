# flake8: noqa E501
from datetime import datetime
import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from config import Config

WDPA_RAW_DATA_FOLDER = Config.WDPA_RAW_DATA_FOLDER
POSTGRES_CONN = Config.POSTGRES_CONN
WDPA_TABLE_NAME = Config.WDPA_TABLE_NAME
SRID = Config.SRID
CELL_SIZE_DEG = Config.CELL_SIZE_DEG
CHUNK_SIZE = 50_000  # Traite 50k lignes à la fois


def download_wdpa_data(**kwargs):
    """
    Version minimale : les fichiers sont déjà présents localement dans data/raw
    Existe comme placeholder pour API.
    """
    print(f"📂 Recherche dans : {WDPA_RAW_DATA_FOLDER}")

    if not os.path.exists(WDPA_RAW_DATA_FOLDER):
        raise FileNotFoundError(
            f"❌ Le dossier {WDPA_RAW_DATA_FOLDER} n'existe pas"
        )  # noqa E501

    files = [
        f for f in os.listdir(WDPA_RAW_DATA_FOLDER) if f.endswith(".csv")
    ]  # noqa E501
    print(f"✅ Trouvé {len(files)} fichiers CSV dans {WDPA_RAW_DATA_FOLDER}")


def load_raw_to_postgis(**kwargs):

    hook = PostgresHook(postgres_conn_id="pfa_postgis")
    conn = hook.get_conn()
    cursor = conn.cursor()

    create_table_sql = """
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE TABLE IF NOT EXISTS raw.stg_wdpa_metadata (
        TYPE TEXT, SITE_ID TEXT, SITE_PID TEXT, SITE_TYPE TEXT,
        NAME_ENG TEXT, NAME TEXT, DESIG TEXT, DESIG_ENG TEXT,
        DESIG_TYPE TEXT, IUCN_CAT TEXT, INT_CRIT TEXT, REALM TEXT,
        REP_M_AREA TEXT, GIS_M_AREA TEXT, REP_AREA TEXT, GIS_AREA TEXT,
        NO_TAKE TEXT, NO_TK_AREA TEXT, STATUS TEXT, STATUS_YR TEXT,
        GOV_TYPE TEXT, GOVSUBTYPE TEXT, OWN_TYPE TEXT, OWNSUBTYPE TEXT,
        MANG_AUTH TEXT, MANG_PLAN TEXT, VERIF TEXT, METADATAID TEXT,
        PRNT_ISO3 TEXT, ISO3 TEXT, SUPP_INFO TEXT, CONS_OBJ TEXT,
        INLND_WTRS TEXT, OECM_ASMT TEXT
    );
    TRUNCATE TABLE raw.stg_wdpa_metadata;
    """

    csv_files = [
        f for f in os.listdir(WDPA_RAW_DATA_FOLDER) if f.endswith(".csv")
    ]  # noqa E501

    try:
        # 2. Création de la table
        cursor.execute(create_table_sql)

        for file in csv_files:
            file_path = os.path.join(WDPA_RAW_DATA_FOLDER, file)
            print(f"Chargement de {file}...")

            with open(file_path, "r", encoding="utf-8") as f:
                # On utilise copy_expert pour envoyer les données
                cursor.copy_expert(
                    sql="""
                    COPY raw.stg_wdpa_metadata
                    FROM STDIN WITH CSV HEADER
                    """,
                    file=f,
                )

        conn.commit()
        print("Table vérifiée et données chargées !")

    except Exception as e:
        conn.rollback()
        print(f"Erreur : {e}")
        raise
    finally:
        cursor.close()
        conn.close()


with DAG(
    dag_id="wdpa_protected_areas_ingestion",
    start_date=datetime(2026, 1, 25),
    schedule_interval="@yearly",
    catchup=False,
    tags=["protected-fishing-areas", "wdpa", "protected-areas"],
) as dag:

    task_download = PythonOperator(
        task_id="download_wdpa_data",
        python_callable=download_wdpa_data,
    )

    task_load = PythonOperator(
        task_id="load_wdpa_to_postgis",
        python_callable=load_raw_to_postgis,
    )

    task_geom_load = BashOperator(
        task_id="ingest_wdpa_shp_to_postgis",
        bash_command="""
        ogr2ogr -f "PostgreSQL" PG:"host={{ params.db_host }} dbname={{ params.db_name }} user={{ params.db_user }} password={{ params.db_password }}" \
        /vsizip/{{ params.file_path }} \
        -nln {{ params.table_name }} \
        -nlt PROMOTE_TO_MULTI \
        -lco GEOMETRY_NAME=geom \
        -lco OVERWRITE=YES \
        -oo ENCODING=LATIN1
        """,
        params={
            "file_path": "/opt/airflow/data/raw/wdpa/WDPA_Feb2026_Public_shp_0.zip",  # noqa E501
            "db_host": Config.POSTGRES_HOST,
            "db_name": "pfa",
            "db_user": "pfa",
            "db_password": "pfa",
            "table_name": "raw.stg_wdpa_polygons",
        },
    )

    run_dbt = BashOperator(
        task_id="run_dbt_transformations_wdpa",
        bash_command="cd /opt/airflow/dbt/protected_fishing_areas && dbt run --profiles-dir .",  # noqa E501
    )

    task_download >> task_load >> task_geom_load >> run_dbt
