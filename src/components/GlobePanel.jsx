import React, { useRef, useState, useEffect } from "react";
import Globe from "react-globe.gl";
import * as d3 from "d3";
import { feature } from "topojson-client";
import ReactCountryFlag from "react-country-flag";
import countries from "i18n-iso-countries";
import enLocale from "i18n-iso-countries/langs/en.json";

countries.registerLocale(enLocale);
function getAlpha2(countryName) {
  const fixes = {
    "Dem. Rep. Congo": "CD",
    "Eq. Guinea": "GQ",
    "Solomon Is.": "SB",
    "Falkland Is.": "FK",
    "Fr. S. Antarctic Lands": "TF",
    "Brunei": "BN"
  };
  return fixes[countryName] || countries.getAlpha2Code(countryName, "en") || "UN";
}

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

  // Function to center globe on a country
  const centerOnCountry = (target) => {
    const centroid = d3.geoCentroid(target);
    if (centroid && globeRef.current) {
      const [lng, lat] = centroid;
      globeRef.current.pointOfView({ lat, lng, altitude: 1.5 }, 1000);
    }
    console.log(target);
  };

  // Handle country search
  const handleSearch = () => {
    const target = countries.find(
      (c) => c.properties.name.toLowerCase() === search.trim().toLowerCase()
    );
    if (!target) {
      alert("Country not found!");
      return;
    }

    handlePolygonClick(target);
  };

  // Handle polygon click
  const handlePolygonClick = (d) => {
    setHighlightCountry(d);
    centerOnCountry(d);
    onSelectCountry && onSelectCountry(d.properties.name);
  };

  // Handle clicks outside the popup
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (highlightCountry) {
        // Check if click is outside the popup card
        const popupElement = event.target.closest('.popup-card');
        if (!popupElement) {
          setHighlightCountry(null);
        }
      }
    };

    if (highlightCountry) {
      document.addEventListener('click', handleClickOutside);
      // Also listen for drag end (when user releases mouse after dragging globe)
      document.addEventListener('mouseup', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('mouseup', handleClickOutside);
    };
  }, [highlightCountry]);

  return (
    <div ref={containerRef} className="w-full h-full relative flex items-center justify-center overflow-hidden">
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
          onPolygonClick={handlePolygonClick}
          width={dimensions.width}
          height={dimensions.height}
        />
      )}

      {/* Popup Card - Centered */}
      {highlightCountry && (
        <div className="absolute top-[70%] left-[80%] transform -translate-x-1/2 -translate-y-1/2 pointer-events-none z-10">
          <div className="popup-card bg-white rounded-xl shadow-xl w-64 overflow-hidden pointer-events-auto">
            <div className="p-3 flex items-center gap-4">
              <div className="flex-shrink-0">
                <ReactCountryFlag 
                  countryCode={getAlpha2(highlightCountry.properties.name)} 
                  svg 
                  style={{ width: '60px', height: '48px' }}
                />
              </div>
              <h3 className="text-lg font-semibold">
                {highlightCountry.properties.name}
              </h3>
            </div>
            <div className="px-3 pb-3">
              <button
                className="mt-2 text-sm text-blue-600 hover:underline"
              >
                Learn More about {highlightCountry.properties.name}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search input */}
      <div className="absolute top-4 right-4 flex items-center gap-2">
        <input
          type="text"
          placeholder="Search country..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-white border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none shadow-md"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-500 text-white px-3 py-1.5 text-sm rounded hover:bg-blue-600 shadow-md h-8 flex items-center justify-center"
        >
          Go
        </button>
      </div>
    </div>
  );
}
