import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(layout="wide")


@st.cache_resource
def get_engine():
    return create_engine("postgresql://pfa:pfa@postgres-data:5432/pfa")


engine = get_engine()

st.title("🚢 Global Fishing Watch x WDPA Analysis")


@st.cache_data
def get_fishing_in_mpas():
    query = """
    WITH fishing AS (
        SELECT
            fishing_hours,
            geartype,
            flag,
            ST_MakeEnvelope(
                lon - 0.05, lat - 0.05,
                lon + 0.05, lat + 0.05, 4326
            ) as fishing_geom
        FROM analytics_marts.fct_fishing_effort
    ),
    mpas AS (
        SELECT site_name, iucn_category, status, geom as mpa_geom
        FROM analytics_marts.fct_protected_areas
    )
    SELECT
        m.site_name,
        m.iucn_category,
        f.geartype,
        f.flag,
        SUM(f.fishing_hours) as total_fishing_hours,
        ST_AsGeoJSON(ST_Centroid(ST_Collect(m.mpa_geom))) as center_point
    FROM fishing f
    JOIN mpas m ON ST_Intersects(f.fishing_geom, m.mpa_geom)
    GROUP BY 1, 2, 3, 4
    ORDER BY total_fishing_hours DESC
    """
    return pd.read_sql(query, engine)


df_impact = get_fishing_in_mpas()

st.subheader("Top des zones protégées sous pression")

if not df_impact.empty:

    st.write("Détail des heures de pêche en zones protégées :")
    st.dataframe(
        df_impact[["site_name", "flag", "geartype", "total_fishing_hours"]]
    )  # noqa E501
