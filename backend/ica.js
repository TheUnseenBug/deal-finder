import puppeteer from "puppeteer";

const icaScraper = async () => {
  const url =
    "https://www.ica.se/erbjudanden/maxi-ica-stormarknad-ljungby-1004102/";
  const browser = await puppeteer.launch({
    executablePath:
      "C:\\Users\\denni\\.cache\\puppeteer\\chrome\\win64-121.0.6167.85\\chrome-win64\\chrome.exe",
    headless: false,
  });
  const page = await browser.newPage();
  let allArticles = [];

  await page.goto(url, {
    waitUntil: "networkidle2",
  });
  await page.waitForSelector(".offer-card__info-container");
  const articles = await page.evaluate(() => {
    const articles = document.querySelectorAll(".offer-card__info-container");

    return Array.from(articles).map((article) => {
      try {
        // Go up to the offer-card to find elements
        const offerCard = article.closest(".offer-card");

        const title = offerCard?.querySelector(".offer-card__title")?.innerText;
        const image = offerCard
          ?.querySelector(".offer-card__image-inner")
          ?.getAttribute("src");
        const priceSplashText = offerCard?.querySelector(
          ".price-splash__text__firstValue"
        )?.innerText;
        const offerText =
          offerCard?.querySelector(".offer-card__text")?.innerText;

        return {
          title: title || null,
          image: image || null,
          price: priceSplashText || null,
          offerText: offerText || null,
        };
      } catch (error) {
        console.error("Error extracting data:", error);
        return null;
      }
    });
  });

  allArticles = allArticles.concat(articles);
  await browser.close();
  return allArticles;
};

export { icaScraper };
