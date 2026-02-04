from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from databases import Database
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://pfa:pfa@postgres-data:5432/pfa"
)  # noqa E501
database = Database(DATABASE_URL)

app = FastAPI(title="PFA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def read_root():
    return {"status": "API is running", "database": "Connected"}


@app.get("/api/health-check")
async def health_check():
    # Test simple pour voir si on peut lire la table générée par dbt
    try:
        query = "SELECT count(*) FROM marts.fct_protected_areas"
        count = await database.fetch_val(query)
        return {"db_status": "OK", "protected_areas_count": count}
    except Exception as e:
        return {"db_status": "Error", "message": str(e)}
