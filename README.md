# Protected Fishing Areas
Analyse de la pression de pêche industrielle sur les zones marines protégées.

Pour ça, on croise les données d'heures

## Data

### Pression de la pêche

J'utilise les données de Global Fishing Watch (Global Fishing Watch. 2025. Global Apparent Fishing Effort Dataset, Version 3.0. doi:10.5281/zenodo.14982712), qui permettent d'évaluer la pression de la pêche. Par simplicité, j'ai décidé de me concentrer exclusivement sur l'année 2024.

Fichiers utilisés : `fleet-monthly-csvs-10-v3-2024` (à télécharger dans data/raw sur https://globalfishingwatch.org/data-download/datasets/public-fishing-effort, login requis)

Schéma :
- date: Date in YYYY-MM-DD format. For the fleet-monthly-10-v3 data, the date corresponds to the first date of the month
- year: year (fleet-monthly-10-v3 only)
- month: month (fleet-monthly-10-v3 only)
- cell_ll_lat: The latitude of the lower left (ll) corner of the grid cell, in decimal degrees (WGS84)
- cell_ll_lon: The longitude of the lower left (ll) corner of the grid cell, in decimal degrees (WGS84)
- flag: Flag state (ISO3 value), based on flag_gfw in fishing-vessels-v3.csv
- geartype: Gear type, based on vessel_class_gfw in fishing-vessels-v3.csv
- hours: Hours that MMSI of this geartype and flag were broadcasting on AIS while present in the grid cell on this day
- fishing_hours: Hours that MMSI of this geartype and flag were broadcasting on AIS in this grid cell on this day and detected as fishing by the GFW fishing detection model
- mmsi_present: Number of MMSI of this flag state and geartype that broadcasted on AIS while present in the grid cell on this day

## Difficultés rencontrées

Initialement, j'ai cherché à faire les transformations basiques dans les DAGs, mais j'ai rencontré plusieurs difficultés techniques.
- Installer GDAL dans le container airflow était très compliqué (incompatibilité de versions python, GDAL, etc).
- Finalement, il était important d'utiliser Python 3.11 et de choisir des versions stables dans requirements.txt.
- J'ai décidé de faire les transformations dans PostgreSQL pour rapidité (100x plus rapide que sur Python !) + lisibilité (respecter les normes DBT d'ingestion RAW -> STAGING, puis faire les transformations en SQL ce qui est plus rapide et efficace).

## Tests

TODO

## CI/CD

J'utilise pre-commit sur le repo pour maintenir la lisibilité du code.

## Version manager

J'utilise UV pour manager mon environnement local ET l'environnement Airflow.

## Archive : comment installer GDAL & autres dépendances sur un container docker ?

J'ai supprimé les imports spécifiques puisque je n'en avais plus besoin, mais voilà une trace du setup qui fonctionnait (au 26-01-26) :

```Dockerfile

FROM apache/airflow:2.8.1-python3.11

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgdal-dev \
    libspatialindex-dev \
    gdal-bin \
    build-essential \
    gcc \
    g++ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

```

```docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  postgres-data:
    image: postgis/postgis:15-3.4
    environment:
      POSTGRES_USER: pfa
      POSTGRES_PASSWORD: pfa
      POSTGRES_DB: pfa
    ports:
      - "5433:5432"
    volumes:
      - postgres_data_pfa:/var/lib/postgresql/data

  airflow:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__LOAD_EXAMPLES: "false"
      AIRFLOW__WEBSERVER__EXPOSE_CONFIG: "true"
      _AIRFLOW_DB_MIGRATE: "true"
      _AIRFLOW_WWW_USER_CREATE: "true"
      _AIRFLOW_WWW_USER_USERNAME: admin
      _AIRFLOW_WWW_USER_PASSWORD: admin
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./data:/opt/airflow/data
      - ./requirements.txt:/requirements.txt
    depends_on:
      - postgres
      - postgres-data
    command: >
      bash -c "
        airflow db migrate &&
        airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com || true &&
        airflow webserver & airflow scheduler
      "

volumes:
  postgres_data:
  postgres_data_pfa:

```

```requirements.txt
fiona==1.9.5
geopandas==0.14.1
shapely==2.0.3
pyproj==3.6.1
psycopg2-binary==2.9.9
pandas==2.2.1
pyarrow>=15.0.0
geoalchemy2>=0.14.0
sqlalchemy>=1.4,<2.0
```
