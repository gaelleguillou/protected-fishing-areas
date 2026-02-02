{{ config(
    materialized='table',
    indexes=[
      {'columns': ['geom'], 'type': 'gist'}
    ]
) }}
with metadata as (
    select * from {{ ref('stg_wdpa__metadata') }}
),

geometries as (
    select * from {{ ref('stg_wdpa__polygons') }}
),

final as (
    select
        -- métadonnées
        m.site_id,
        m.site_name,
        m.designation,
        m.designation_type,
        m.iucn_category,
        m.status,
        m.status_year,
        m.iso3,
        m.governance_type,
        m.management_authority,

        -- géométrie
        g.geom,
        st_area(g.geom::geography) / 1000000 as calculated_area_km2

    from metadata m
    inner join geometries g on m.site_id = g.site_id
)

select * from final
