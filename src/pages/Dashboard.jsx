import GlobePanel from "../components/GlobePanel";
import InfoPanel from "../components/InfoPanel";
import { useState } from "react";

export default function Dashboard() {
  const [country, setCountry] = useState(null);

  return (
    <div className="flex flex-col md:flex-row h-screen">
      {/* Left info panel */}
      <div className="w-full md:w-1/3 bg-white shadow-md p-6 overflow-y-auto">
        <InfoPanel country={country} />
      </div>

      {/* Right globe panel */}
      <div className="flex-1 bg-gray-200">
        <GlobePanel onSelectCountry={setCountry} />
      </div>
    </div>
  );
}
