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
      <div className="bg-white rounded-xl shadow-2xl w-[550px] h-[360px] overflow-hidden relative" onClick={(e) => e.stopPropagation()}>
        {/* Close Button - Top Right */}
        <button
          onClick={onClose}
          className="absolute top-2 right-2 z-10 text-gray-500 hover:text-gray-700 transition-colors"
          aria-label="Close"
        >
          <svg className="w-4 h-4 text-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center gap-3">
          <div className="flex-shrink-0">
            <ReactCountryFlag 
              countryCode={getAlpha2(country.properties.name)} 
              svg 
              style={{ width: '50px', height: '38px' }}
            />
          </div>
          <h2 className="text-xl font-bold text-gray-800">
            {country.properties.name}
          </h2>
        </div>

        {/* Content - Two Column Layout */}
        <div className="px-6 py-3 flex gap-6 overflow-y-auto" style={{ height: 'calc(360px - 90px)' }}>
          {/* Left Side */}
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Introduction</h3>
            <p className="text-gray-600">
              Country introduction will be displayed here...
            </p>
          </div>

          {/* Right Side - Ratings */}
          <div className="w-48 border-l border-gray-300 pl-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Ratings</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Rating 1</span>
                  <span className="font-semibold">0/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Rating 2</span>
                  <span className="font-semibold">0/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                </div>
              </div>
                             <div>
                 <div className="flex justify-between text-sm mb-1">
                   <span className="text-gray-600">Rating 3</span>
                   <span className="font-semibold">0/10</span>
                 </div>
                 <div className="w-full bg-gray-200 rounded-full h-2">
                   <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                 </div>
               </div>
               <div>
                 <div className="flex justify-between text-sm mb-1">
                   <span className="text-gray-600">Rating 4</span>
                   <span className="font-semibold">0/10</span>
                 </div>
                 <div className="w-full bg-gray-200 rounded-full h-2">
                   <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                 </div>
               </div>
               <div>
                 <div className="flex justify-between text-sm mb-1">
                   <span className="text-gray-600">Rating 5</span>
                   <span className="font-semibold">0/10</span>
                 </div>
                 <div className="w-full bg-gray-200 rounded-full h-2">
                   <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                 </div>
               </div>
             </div>
                    </div>
        </div>
      </div>
    </div>
  );
}
