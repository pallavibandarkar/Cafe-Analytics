import "./Navbar.css";
import { assets } from "../../assets/assets.js";
import { useNavigate } from "react-router-dom"; 
export default function Navbar({ isLoggedIn, setIsLoggedIn, setIsLoginPopupVisible }) {
    const navigate = useNavigate(); // Create a navigate function

    const handleLogout = () => {
        setIsLoggedIn(false); // Update the logged-in state
        navigate("/"); // Navigate to the home page
    };

    return (
        <div className="Navbar">
            <div className="Nav-left">
                <img className="logo" src={assets.Coffe_Logo} alt="Coffee Logo" />
                <img className="logow" src={assets.coffee_w} alt="Coffee Logo White" />
            </div>

            <ul className="Nav-menu">
                <li><a href="#">Home</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#contact">Contact Us</a></li>
                <li><a href="#">Insights Dashboard</a></li>
                <li><a href="#features">About Us</a></li>
            </ul>

            <div className="Navbar-right">
                {!isLoggedIn && (
                    <button onClick={() => setIsLoginPopupVisible(true)}>Sign Up</button>
                )}
                {isLoggedIn && (
                    <button onClick={handleLogout}>Logout</button>
                )}
            </div>
        </div>
    );
}
