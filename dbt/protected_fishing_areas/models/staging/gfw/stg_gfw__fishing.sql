with source as (
    select * from {{ source('raw_data', 'stg_gfw_fishing') }}
),

renamed as (
    select
        date::date as fishing_date,
        year::int as fishing_year,
        geartype,
        flag,
        fishing_hours::float as fishing_hours,
        cell_ll_lat::float as lat,
        cell_ll_lon::float as lon
    from source
)

select * from renamed
