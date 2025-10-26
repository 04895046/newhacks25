import ResizablePanel from "../components/ResizablePanel";
import Navbar from "../components/Navbar";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [country, setCountry] = useState(null);
  const [username, setUsername] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    // Get username from localStorage (set during login)
    const storedUsername = localStorage.getItem("username") || "User";
    setUsername(storedUsername);

    // Check if user is authenticated
    const token = localStorage.getItem("authToken");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  return (
    <div className="flex flex-col h-screen">
      {/* Navbar */}
      <Navbar username={username} />
      
      {/* Content area */}
      <ResizablePanel country={country} onSelectCountry={setCountry} />
    </div>
  );
}
