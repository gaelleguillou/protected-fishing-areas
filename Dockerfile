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
