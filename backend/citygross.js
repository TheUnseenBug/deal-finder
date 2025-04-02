import puppeteer from "puppeteer";

const cityGrossBlogScraper = async () => {
  const url = "https://www.citygross.se/matvaror/veckans-erbjudande";
  const elements = ".productcard-container"; // Selector for each product card
  const titleElement = ".details__name"; // Selector for the title within the card
  const browser = await puppeteer.launch({
    executablePath:
      "C:\\Users\\denni\\.cache\\puppeteer\\chrome\\win64-121.0.6167.85\\chrome-win64\\chrome.exe",
    headless: false,
  });
  const page = await browser.newPage();
  let allArticles = [];
  let currentPage = 1;
  const maxPages = 13; // Set a maximum number of pages to scrape to prevent infinite loops

  while (currentPage <= maxPages) {
    await page.goto(`${url}?page=${currentPage}`, {
      waitUntil: "networkidle2",
    });
    await page.waitForSelector(".productcard-container");
    const articles = await page.evaluate(
      (allElementsSelector, titleSelector) => {
        const articles = document.querySelectorAll(allElementsSelector);
        console.log("Number of articles found:", articles.length); // Check if any articles are found

        return Array.from(articles)
          .map((article) => {
            try {
              const title = article.querySelector(titleSelector)?.innerText;
              const price =
                article.querySelector(".sc-dEVLtI.fYylmA")?.innerText;
              const priceSuffix =
                article.querySelector(".sc-gJqSRm.jvNleb")?.innerText;
              const image = article.querySelector(
                ".c-progressive-picture__img"
              )?.srcset;
              return { title, price, image, priceSuffix };
            } catch (error) {
              console.error("Error extracting data:", error);
              return null; // Or some other error indicator
            }
          })
          .filter((article) => article !== null);
      },
      elements,
      titleElement
    );
    allArticles = allArticles.concat(articles);
    currentPage++;
  }
  await browser.close();
  return allArticles;
};
export { cityGrossBlogScraper };
