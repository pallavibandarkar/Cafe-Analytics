import React, { useState } from "react";
import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar/Navbar.jsx";
import Home from "./pages/Home/Home.jsx";
import Welcome from "./components/Welcome/Welcome.jsx";
import Login from "./components/Login/Login.jsx";

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false); // Track if the user is logged in
    const [isLoginPopupVisible, setIsLoginPopupVisible] = useState(false); // Track visibility of login popup

    return (
        <>
            <Navbar 
                isLoggedIn={isLoggedIn} 
                setIsLoggedIn={setIsLoggedIn} 
                setIsLoginPopupVisible={setIsLoginPopupVisible} // Pass the function to control popup
            />
            {/* Render Login popup only if it's visible */}
            {isLoginPopupVisible && (
                <Login 
                    setIsLoggedIn={setIsLoggedIn} 
                    setIsLoginPopupVisible={setIsLoginPopupVisible} // Pass this to close the popup
                />
            )}
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/welcome" element={<Welcome />} /> {/* Add this route */}
            </Routes>
        </>
    );
}

export default App;
