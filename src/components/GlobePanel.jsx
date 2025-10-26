import React, { useRef, useState, useEffect } from "react";
import Globe from "react-globe.gl";
import * as d3 from "d3";
import { feature } from "topojson-client";

export default function GlobePanel({ onSelectCountry }) {
  const globeRef = useRef();
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [countries, setCountries] = useState([]);
  const [search, setSearch] = useState("");
  const [highlightCountry, setHighlightCountry] = useState(null);

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

  // Handle country search
  const handleSearch = () => {
    const target = countries.find(
      (c) => c.properties.name.toLowerCase() === search.trim().toLowerCase()
    );
    if (!target) {
      alert("Country not found!");
      return;
    }

    setHighlightCountry(target);
    const { geometry } = target;

    // Compute centroid of the country to rotate the globe there
    const centroid = d3.geoCentroid(target);
    if (centroid && globeRef.current) {
      const [lng, lat] = centroid;
      globeRef.current.pointOfView({ lat, lng, altitude: 1.5 }, 1000);
    }

    onSelectCountry && onSelectCountry(target.properties.name);
  };

  return (
    <div ref={containerRef} className="w-full h-full flex items-center justify-center overflow-hidden">
      {dimensions.width > 0 && dimensions.height > 0 && (
        <Globe
          ref={globeRef}
          globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
          backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
          polygonsData={countries}
          polygonCapColor={(d) => d === highlightCountry ? "orange" : "rgba(0, 255, 0, 0.3)"}
          polygonSideColor={() => "rgba(0, 100, 0, 0.15)"}
          polygonStrokeColor={() => "#111"}
          polygonLabel={(d) => `<b>${d.properties.name}</b>`}
          polygonAltitude={(d) => (d === highlightCountry ? 0.012 : 0.007)}
          onPolygonClick={(d) => {
            setHighlightCountry(d);
            onSelectCountry && onSelectCountry(d.properties.name);
          }}
          width={dimensions.width}
          height={dimensions.height}
        />
      )}

      {/* Search input */}
      <div className="absolute top-4 right-4 bg-white bg-opacity-80 rounded-lg p-2 shadow-md flex items-center gap-2">
        <input
          type="text"
          placeholder="Search country..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-500 text-white px-3 py-1 text-sm rounded hover:bg-blue-600"
        >
          Go
        </button>
      </div>
    </div>
  );
}
