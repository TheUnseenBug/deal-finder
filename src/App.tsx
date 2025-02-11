import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('');
  const [__scrapedData, setScrapedData] = useState(null);
  const [error, setError] = useState(null);

  const handleScrape = async () => {
    setError(null); // Clear any previous errors

    try {
      const response = await fetch(`http://localhost:3001/scrape?url=${url}`);

      if (!response.ok) {
        // Handle HTTP errors (e.g., 400, 500)
        const errorData = await response.json();
        throw new Error(errorData.error || 'Request failed');
      }

      const data = await response.json();
      console.log(data)
      setScrapedData(data);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.message);
      setScrapedData(null); // Clear any previous data
    }
  };
  return (
    <>
 <div>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL to scrape"
      />
      <button onClick={handleScrape}>Scrape</button>

      {error && <div style={{ color: 'red' }}>Error: {error}</div>}

    </div>
    </>
  )
}

export default App
