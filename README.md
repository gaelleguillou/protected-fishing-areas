# Protected Fishing Areas

Analyse de la pression de pêche industrielle sur les zones marines protégées. Pour ça, on cherche à croiser les données de pression de la pêche (de Global Fishing Watch) avec les données de zones marines protégées.

Projet en cours, en voici l'évolution :
- [x] Initialiser le projet avec des bonnes pratiques de CI/CD (pre-commit hooks)
- [x] Configurer un container Docker pour faire tourner Airflow et PostGIS
- [x] Configurer le projet DBT avec les bonnes pratiques (modèles staging, intermediate et analytics)
- [x] Créer les schémas DBT et la table `fct_fishing_effort.sql` qui transforme les lon/lat en Polygones géométriques (anticipant les besoins analytiques)
- [x] Créer un DAG dans Airflow qui : vérifie le téléchargement des données dans data/raw > load les données GFW dans Postgres (PostGIS) > lance les transformations DBT
- [x] Intégrer les données géographiques des ZMP (Zones Marines Protégées) selon une logique similaire
- [ ] Développer des tests dbt pour vérifier la correcte intégration des données et leur cohérence (type vérifier les formats longitude / latitude, etc)
- [ ] Créer une page interactive de cartographie et analyse des pressions de la pêche sur les ZMP

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

### Zones maritimes protégées mondiales

UNEP-WCMC and IUCN (2026), Protected Planet: The World Database on Protected Areas (WDPA) and World Database on Other Effective Area-based Conservation Measures (WD-OECM) [Online], January 2026, Cambridge, UK: UNEP-WCMC and IUCN. Available at: www.protectedplanet.net.

A télécharger depuis : https://www.protectedplanet.net/en/thematic-areas/marine-protected-areas et mettre dans le dossier data/raw/ (modifier le chemin dans Config.py) (le fichier csv pour les metadonnées, .shp pour les polygones)

## Difficultés rencontrées

Initialement, j'ai cherché à faire les transformations basiques dans les DAGs, mais j'ai rencontré plusieurs difficultés techniques.
- Installer GDAL dans le container airflow était très compliqué (incompatibilité de versions python, GDAL, etc).
- Finalement, il était important d'utiliser Python 3.11 et de choisir des versions stables dans requirements.txt.
- J'ai décidé de faire les transformations dans PostgreSQL pour rapidité (100x plus rapide que sur Python !) + lisibilité (respecter les normes DBT d'ingestion RAW -> STAGING, puis faire les transformations en SQL ce qui est plus rapide et efficace).

## Tests

TODO

## CI/CD

J'utilise pre-commit sur le repo pour maintenir la lisibilité du code.
