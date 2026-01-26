with staging as (
    select * from {{ ref('stg_gfw__fishing') }}
)

select
    *,
    -- On crée le polygone dynamiquement en SQL
    ST_MakeEnvelope(
        lon - (0.1 / 2), -- Remplace 0.1 par ta variable CELL_SIZE_DEG
        lat - (0.1 / 2),
        lon + (0.1 / 2),
        lat + (0.1 / 2),
        4326
    )::geometry(Polygon, 4326) as geometry
from staging
