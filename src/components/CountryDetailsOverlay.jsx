import React from "react";
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
    "Brunei": "BN",
    "Central African Rep.": "CF",
    "Somaliland": "SO"
  };
  return fixes[countryName] || countries.getAlpha2Code(countryName, "en") || "UN";
}

export default function CountryDetailsOverlay({ country, onClose }) {
  if (!country) return null;

  return (
    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl w-96 max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center gap-4">
          <div className="flex-shrink-0">
            <ReactCountryFlag 
              countryCode={getAlpha2(country.properties.name)} 
              svg 
              style={{ width: '80px', height: '60px' }}
            />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">
            {country.properties.name}
          </h2>
        </div>

        {/* Content - Placeholder for now */}
        <div className="p-6">
          <p className="text-gray-600">Country details will be displayed here...</p>
        </div>

        {/* Close Button */}
        <div className="p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
