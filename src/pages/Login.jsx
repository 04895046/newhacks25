import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const url = isSignup ? "/api/register/" : "/api/login/";
      const res = await axios.post(url, { username, password });

      // For login, save the token
      if (!isSignup) {
        localStorage.setItem("authToken", res.data.token);
      }

      // Navigate to dashboard
      navigate("/dashboard");
    } catch (err) {
      alert("Invalid username or password");
      setUsername("");
      setPassword("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center fixed inset-0 w-screen h-screen bg-gradient-to-br from-blue-200 to-blue-500">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-80">
        <h2 className="text-2xl font-bold mb-4 text-center">
          {isSignup ? "Sign Up" : "Log In"}
        </h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input
            type="username"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="border rounded p-2"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="border rounded p-2"
          />
          <button 
            type="submit" 
            disabled={isLoading}
            className="bg-blue-600 text-blue py-2 rounded flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading && (
              <svg className="animate-spin h-5 w-5 text-blue" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            {isLoading ? (isSignup ? "Signing Up..." : "Logging In...") : (isSignup ? "Create Account" : "Log In")}
          </button>
        </form>
        <p
          className="text-sm text-center mt-3 cursor-pointer text-blue-600"
          onClick={() => setIsSignup(!isSignup)}
        >
          {isSignup ? "Already have an account? Log in" : "No account? Sign up"}
        </p>
      </div>
    </div>
  );
}
