import React, { useRef, useState, useEffect } from "react";
import Globe from "react-globe.gl";
import { feature } from "topojson-client";

export default function GlobePanel({ onSelectCountry }) {
  const globeRef = useRef();
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [countries, setCountries] = useState([]);

  // Load country polygons (GeoJSON) once
  useEffect(() => {
    fetch("https://unpkg.com/world-atlas@2/countries-110m.json")
      .then((res) => res.json())
      .then((topojsonData) => {
        // Convert TopoJSON to GeoJSON
        const geoJson = feature(topojsonData, topojsonData.objects.countries).features;
        setCountries(geoJson);
      });
  }, []);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };

    // Initial size
    updateDimensions();

    // Resize observer to track container size changes
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    // Fallback to window resize listener
    window.addEventListener("resize", updateDimensions);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener("resize", updateDimensions);
    };
  }, []);

  return (
    <div ref={containerRef} className="w-full h-full flex items-center justify-center overflow-hidden">
      {dimensions.width > 0 && dimensions.height > 0 && (
        <Globe
          ref={globeRef}
          globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
          backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
          polygonsData={countries}
          polygonCapColor={(d) => "rgba(0, 255, 0, 0.3)"}
          polygonSideColor={() => "rgba(0, 100, 0, 0.15)"}
          polygonStrokeColor={() => "#111"}
          polygonLabel={(d) => `<b>${d.properties.name}</b>`}
          polygonAltitude={0.01}
          onPolygonClick={(d) => {
            onSelectCountry && onSelectCountry(d.properties.name);
          }}
          width={dimensions.width}
          height={dimensions.height}
        />
      )}
    </div>
  );
}
