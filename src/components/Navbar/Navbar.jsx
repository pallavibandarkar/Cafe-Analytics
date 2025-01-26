import "./Navbar.css";
import { assets } from "../../assets/assets.js";
import { useNavigate } from "react-router-dom";
import { Link } from 'react-router-dom';

export default function Navbar({ isLoggedIn, setIsLoggedIn, setIsLoginPopupVisible }) {
    const navigate = useNavigate(); // Create a navigate function

    const handleLogout = () => {
        // Clear authentication-related data (example: clearing local storage or cookies)
        localStorage.removeItem("userToken"); // Remove user token
        localStorage.removeItem("userData");  // Optional: Remove user data if stored
        setIsLoggedIn(false); // Update the logged-in state
        navigate("/"); // Navigate to the home page
    };

    return (
        <div className="Navbar">
            {/* Left Section: Logo */}
            <div className="Nav-left">
                <img className="logo" src={assets.Coffe_Logo} alt="Coffee Logo" />
                <img className="logow" src={assets.coffee_w} alt="Coffee Logo White" />
            </div>

            {/* Center Section: Navigation Menu */}
            {!isLoggedIn &&(
            <ul className="Nav-menu">
                <li><a href="#">Home</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#contact">Contact Us</a></li>
                <li><a href="#">Insights Dashboard</a></li>
                <li><a href="#features">About Us</a></li>
            </ul>
            )}
            {isLoggedIn && (
             <ul className="Nav-menu">
            <li><Link to="/welcome">Home</Link></li>
            <li><Link to="#">Insights Dashboard</Link></li>
        </ul>
        )}
            
            {/* Right Section: Login/Logout Button */}
            <div className="Navbar-right">
                {!isLoggedIn && (
                    <button onClick={() => setIsLoginPopupVisible(true)}>
                        Sign Up
                    </button>
                )}
                {isLoggedIn && (
                    <button onClick={handleLogout}>
                        Logout
                    </button>
                )}
            </div>
        </div>
    );
}
