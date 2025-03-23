import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import './w.css'
import { assets } from "../../assets/assets";
export default function Welcome() {
    const username = localStorage.getItem('username');
    const navigate = useNavigate(); 

    useEffect(() => {
        console.log("Current username:", username); 
    }, [username]);

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

            {username && (
                <div className="dashboard">
                    <div className="featured">
                        <img src={assets.Product_Performance}/>
                        <h5>Product Performance</h5>
                        <p>We analyze customer reviews to understand opinions about each product. 
                            A pie chart shows the percentage of positive, negative, and neutral reviews.
                        </p>
                    </div>
                    <div className="featured">
                        <img src={assets.mba1}/>
                        <h5>Product Recommendation</h5>
                        <p>Based on customer buying patterns, we suggest the best product combinations. 
                            This helps customers find products they are likely to buy together.
                        </p>
                    </div>
                    <div className="featured">
                        <img src={assets.Analytic_Dashboard}/>
                        <h5>Analytic Dashboard</h5>
                        <p>We provide insights like top-selling products, sales trends over months,
                        and payment method distribution, helping businesses make informed decisions.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
