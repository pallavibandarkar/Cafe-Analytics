import React from "react";

export default function Welcome() {
    const username = localStorage.getItem('username')
    return (

        <div className="welcome-page">
            <h1>Welcome, {username}!</h1>
            <p>You have successfully logged in.</p>
        </div>
    );
}
