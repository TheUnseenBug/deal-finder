export const scrapeData = async (url: string) => {
  try {
    const response = await fetch(`http://localhost:3001/scrape?url=${url}`);

    if (!response.ok) {
      // Handle HTTP errors (e.g., 400, 500)
      const errorData = await response.json();
      throw new Error(errorData.error || "Request failed");
    }

    const data = await response.json();
    console.log(data);
    return data;
  } catch (err) {
    console.error("Error fetching data:", err);
    throw new Error(err.message);
  }
};
