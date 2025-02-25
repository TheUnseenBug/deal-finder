import { useEffect, useState } from "react";
import "./App.css";
import { scrapeData } from "./helpers/scraper"; // Import the scrapeData function
import ProductCard from "./components/product-card";
import Product from "./types/product";

function App() {
  const [scrapedData, setScrapedData] = useState(null);
  const [error, setError] = useState(null);

  const ica =
    "https://www.ica.se/erbjudanden/maxi-ica-stormarknad-ljungby-1004102/";
  const cityGross = "https://www.citygross.se/matvaror/veckans-erbjudande";
  const willys = "https://www.willys.se/erbjudanden/butik";

  const handleScrape = async (url: string) => {
    setError(null); // Clear any previous errors

    try {
      const data = await scrapeData(url); // Use the imported function
      setScrapedData(data);
    } catch (err: any) {
      console.error("Error fetching data:", err);
      setError(err.message);
      setScrapedData(null); // Clear any previous data
    }
  };

  useEffect(() => {
    handleScrape(ica);
  }, []);

  return (
    <>
      <main className="max-w-5xl m-auto">
        <section className="grid grid-cols-6 gap-2 ">
          {scrapedData?.map((data: Product) => (
            <ProductCard data={data} />
          ))}
        </section>
      </main>
    </>
  );
}

export default App;
