import { useNavigate } from "react-router-dom";

export default function Navbar({ username }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow-lg px-6 py-2 border-b border-gray-200">
      <div className="flex items-center justify-between">
        {/* Left spacer */}
        <div className="flex-1"></div>
        
        {/* Center - Project Name */}
        <div className="flex-1 flex justify-center">
          <h1 className="text-xl font-bold text-blue-600">Travel Explorer</h1>
        </div>
        
        {/* Right - Username and Logout */}
        <div className="flex-1 flex justify-end items-center gap-4">
          <span className="text-gray-700">
            Welcome, <span className="font-semibold">{username}</span>
          </span>
          <button
            onClick={handleLogout}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
