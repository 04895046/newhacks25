import { useState } from 'react';

export default function InfoPanel({ country }) {
  const [formData, setFormData] = useState({
    destinationRegion: '',
    tripLength: '',
    budget: '',
    preferences: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch(`https://evenonvodkathiswill.work/api/itineraries/generate/`, {
      method: 'POST',
      headers: {
        'Authorization': `${import.meta.env.GEMINI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        destination: formData.destinationRegion,
        tripLength: formData.tripLength,
        "currentLocation": {
          "latitude": 43.6532,
          "longitude": -79.3832
        },
        budget: formData.budget,
        preferences: formData.preferences
      })
    });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Trip plan:', result);
      alert('Trip planned! Check console for details.');
    } catch (error) {
      console.error('Error calling API:', error);
      alert('Failed to connect to backend service: ' + error.message);
    }
  };

  return (
    <div className="h-full">
      <h1 className="text-2xl font-bold mb-6 text-gray-800">Trip Planner</h1>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Destination Region
          </label>
          <input
            type="text"
            name="destinationRegion"
            value={formData.destinationRegion}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Southeast Asia, Europe"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Trip Length
          </label>
          <input
            type="text"
            name="tripLength"
            value={formData.tripLength}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 7 days, 2 weeks"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Budget
          </label>
          <input
            type="text"
            name="budget"
            value={formData.budget}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., $2000, moderate"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Preferences
          </label>
          <textarea
            name="preferences"
            value={formData.preferences}
            onChange={handleChange}
            rows="4"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Adventure travel, cultural sites, beach resorts..."
          />
        </div>

        <button
          onClick={handleSubmit}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          Plan My Trip
        </button>
      </div>

      {country && (
        <div className="mt-6 bg-blue-50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">{country.name}</h2>
          <p className="text-gray-600 text-sm">Selected from globe</p>
        </div>
      )}
    </div>
  );
}
