import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import './w.css'
export default function Welcome() {
    const username = localStorage.getItem('username');
    const navigate = useNavigate(); // Initialize the navigate function

    useEffect(() => {
        console.log("Current username:", username); // Debugging: Check username in localStorage
    }, [username]);

    // Navigation functions for each button
    const goToTransactions = () => navigate("/transactions");
    const goToReviews = () => navigate("/reviews");
    const goToSentiment = () => navigate("/s");
    const goToRecommend = () => navigate("/recommend");

    return (
        <div className="welcome-page">
            <h1>Welcome, {username ? username : "Guest"}!</h1>
            {username ? (
                <p>You have successfully logged in.</p>
            ) : (
                <p>Please log in to access your account.</p>
            )}

            {/* Debugging: Ensure the buttons are being displayed */}
            {username && (
                <div className="navigation-buttons">
                    
                    <button onClick={goToSentiment}>Go to Sentiment</button>
                    <button onClick={goToRecommend}>Go to Recommend</button>
                    <button onClick={goToTransactions}>Go to Transactions</button>
                    <button onClick={goToReviews}>Go to Reviews</button>
                </div>
            )}
        </div>
    );
}
