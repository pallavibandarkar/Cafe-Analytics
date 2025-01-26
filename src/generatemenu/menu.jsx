import { useState } from "react";
import axios from "axios";
import './menu.css';

const RecommendationForm = () => {
  const [userId, setUserId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sessionIndex, setSessionIndex] = useState(0); // Keep track of session index for pagination
  const [finished, setFinished] = useState(false); // Flag to check if data is finished

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Send the request to the backend with session index
      const response = await axios.post(
        'http://localhost:5000/recommend', // Flask server endpoint
        { user_id: userId, session_index: sessionIndex }, // Include session index in the request
        { responseType: 'blob' } // Expect a binary response (PDF)
      );

      // If no more data is returned, set the finished flag
      if (response.data.message === "No more data") {
        setFinished(true);
      } else {
        // Update session index with each batch
        setSessionIndex(sessionIndex + 20); // Increment session index by batch size (20)
        
        // Download the PDF
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = 'filtered_recommendations.pdf';  // Name of the PDF file
        link.click();
      }
    } catch (err) {
      setError('Failed to fetch recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form className='recommend' onSubmit={handleSubmit}>
        <label>
          User ID:
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={loading || finished}>
          {loading ? 'Loading...' : 'Download Menu Card'}
        </button>
        <br />
        {error && <div style={{ color: 'red' }}>{error}</div>}
        {finished && <div>No more data available.</div>}
      </form>
    </div>
  );
};

export default RecommendationForm;
