export default function InfoPanel({ country }) {
  return (
    <div className="h-full">
      <h1 className="text-2xl font-bold mb-6 text-gray-800">Global Dashboard</h1>
      
      {country ? (
        <div className="bg-blue-50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">{country}</h2>
          <p className="text-gray-600">Population: {country.population?.toLocaleString() || 'N/A'}</p>
          <p className="text-gray-600">Capital: {country.capital || 'N/A'}</p>
          <p className="text-gray-600">Region: {country.region || 'N/A'}</p>
        </div>
      ) : (
        <div className="text-center text-gray-500 mt-8">
          <p>Click on a country on the globe to view details</p>
        </div>
      )}
      
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span>Total Countries:</span>
            <span className="font-semibold">195</span>
          </div>
          <div className="flex justify-between">
            <span>Active Users:</span>
            <span className="font-semibold">1,234</span>
          </div>
          <div className="flex justify-between">
            <span>Data Points:</span>
            <span className="font-semibold">50,000+</span>
          </div>
        </div>
      </div>
    </div>
  );
}
