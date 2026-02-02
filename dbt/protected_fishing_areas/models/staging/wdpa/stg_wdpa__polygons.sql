with source as (

    select * from {{ source('raw_data', 'stg_wdpa_polygons') }}

),

renamed as (

    select
        -- identifiants
        ogc_fid as internal_id,
        site_id::bigint as site_id,
        site_pid as site_parent_id,

        -- infos de base
        name as site_name,
        iso3,

        -- statut et année
        status,
        nullif(status_yr, '0')::int as status_year,

        -- géométrie
        st_makevalid(geom) as geom,

        -- surfaces
        nullif(trim(rep_area::text), '')::float as reported_area,
        nullif(trim(rep_m_area::text), '')::float as reported_marine_area

    from source

)

select * from renamed
