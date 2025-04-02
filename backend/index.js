import express from "express"; // Use ES modules
import cors from "cors"; // Import the cors middleware
import { cityGrossBlogScraper } from "./citygross.js";
import { icaScraper } from "./ica.js";
import { willysScraper } from "./willys.js";
import { LidlScraper } from "./lidl.js";

const app = express();
const port = 3001; // Or any port you prefer

// Configure CORS
const corsOptions = {
  origin: "http://localhost:5173", // Allow requests from your React app's origin
  optionsSuccessStatus: 200, // Some legacy browsers (IE11, various SmartTVs) choke on 204
};

app.use(cors(corsOptions)); // Enable CORS for all routes

// Route to scrape a URL provided as a query parameter
app.get("/scrape", async (req, res) => {
  const url = req.query.url; // Extract the URL from the query parameters

  if (!url) {
    return res.status(400).send({ error: "URL parameter is required" });
  }

  try {
    const scrapedData = await LidlScraper();
    console.log(scrapedData);
    res.json(scrapedData); // Send the scraped data as JSON
  } catch (error) {
    console.error("Error during scraping:", error);
    res.status(500).send({ error: "Scraping failed", details: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
