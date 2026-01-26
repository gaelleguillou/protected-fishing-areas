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

Installer GDAL dans le container airflow était très compliqué (incompatibilité de versions python, GDAL, etc).

Finalement, il était important d'utiliser Python 3.11 et de choisir des versions stables dans requirements.txt.
