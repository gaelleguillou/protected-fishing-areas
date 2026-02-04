import React, { useEffect, useState } from 'react';
import Map, { Source, Layer } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/protected-areas')
      .then(res => res.json())
      .then(json => setData(json[0])); // Récupère le GeoJSON de FastAPI
  }, []);

  const layerStyle = {
    id: 'mpas-fill',
    type: 'fill',
    paint: { 'fill-color': '#088', 'fill-opacity': 0.5 }
  };

  return (
    <Map
      initialViewState={{ longitude: 0, latitude: 20, zoom: 2 }}
      style={{ width: '100vw', height: '100vh' }}
      mapStyle="https://demotiles.maplibre.org/style.json"
    >
      {data && (
        <Source type="geojson" data={data}>
          <Layer {...layerStyle} />
        </Source>
      )}
    </Map>
  );
}

export default App;
