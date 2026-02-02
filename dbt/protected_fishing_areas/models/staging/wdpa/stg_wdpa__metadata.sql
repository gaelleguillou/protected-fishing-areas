with source as (

    select * from {{ source('raw_data', 'stg_wdpa_metadata') }}

),

renamed as (

    select
        -- identifiants
        site_id::bigint as site_id,
        site_pid as site_parent_id,
        metadataid::int as metadata_id,

        -- noms et descriptions
        name as site_name,
        name_eng as site_name_eng,
        desig as designation,
        desig_eng as designation_eng,
        desig_type as designation_type,

        -- catégories
        type as area_type,
        site_type,
        iucn_cat as iucn_category,
        int_crit as international_criteria,
        realm,

        -- géographie
        nullif(rep_m_area, '')::float as reported_marine_area,
        nullif(gis_m_area, '')::float as gis_marine_area,
        nullif(rep_area, '')::float as reported_area,
        nullif(gis_area, '')::float as gis_area,

        -- no take
        no_take as no_take_status,
        nullif(no_tk_area, '')::float as no_take_area,

        -- statut et année
        status,
        nullif(status_yr, '0')::int as status_year, -- '0' signifie souvent année inconnue dans WDPA

        -- gouvernance
        gov_type as governance_type,
        govsubtype as governance_sub_type,
        own_type as ownership_type,
        mang_auth as management_authority,
        mang_plan as management_plan,

        -- iso
        iso3,
        prnt_iso3 as parent_iso3,

        -- autres
        verif as verification_status,
        supp_info as supplementary_info,
        cons_obj as conservation_objectives,
        inlnd_wtrs as inland_waters_status,
        oecm_asmt as oecm_assessment

    from source

)

select * from renamed
