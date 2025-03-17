import React, { useState } from "react";
import axios from "axios";
import "./menu.css";

const RecommendationForm = () => {
  const [recommendations, setRecommendations] = useState([]);


  const fetchRecommendations = async () => {
    try {
      const response = await axios.post("http://localhost:8080/recommend");
      setRecommendations(response.data.recommended_coffees);
       // Ensure sessionIndex is in sync with Flask
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    }
  };

  
const downloadPDF = async () => {
  try {
    const response = await axios.get("http://localhost:8080/download_pdf", {
      responseType: "blob", // Ensure response is binary
    });

    if (!response.data) {
      throw new Error("PDF response is empty.");
    }

    const pdfBlob = new Blob([response.data], { type: "application/pdf" });
    const pdfUrl = URL.createObjectURL(pdfBlob);

    // Create and trigger a hidden anchor tag
    const link = document.createElement("a");
    link.href = pdfUrl;
    link.setAttribute("download", "filtered_recommendations.pdf");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

  } catch (error) {
    console.error("Error downloading PDF:", error.message || error);
  }
};


  return (
    <div>
      <h2>Recommended Coffees</h2>
      <div className="button-container">
      <button className="reccomend" onClick={fetchRecommendations}>Get Recommendations</button>
      <button className="download" onClick={downloadPDF} >
        Download Menu Card PDF
      </button>
      </div>
      <ul>
        {recommendations.map((coffee, index) => (
          <li key={index}>{coffee}</li>
        ))}
      </ul>
      
    </div>
  );
};

export default RecommendationForm;
