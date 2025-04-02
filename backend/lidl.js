import puppeteer from "puppeteer";

const LidlScraper = async () => {
  const url =
    "https://www.lidl.se/c/mandag-soendag/a10066884?channel=store&tabCode=Current_Sales_Week";
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

  async function rejectCookies(page) {
    try {
      const rejectButtonSelector = "#onetrust-reject-all-handler";

      // Wait for the button to be present in the DOM
      await page.waitForSelector(rejectButtonSelector, { timeout: 5000 });

      // Wait for the button to be visible
      await page.waitForSelector(rejectButtonSelector, {
        visible: true,
        timeout: 5000,
      });

      // Force the click using evaluate
      await page.evaluate((selector) => {
        const button = document.querySelector(selector);
        if (button) {
          button.click();
          console.log("Rejected all cookies.");
        } else {
          console.error("Reject cookies button not found.");
        }
      }, rejectButtonSelector);
    } catch (error) {
      console.error("Error rejecting cookies:", error);
    }
  }
  await rejectCookies(page);
  await page.waitForSelector(
    ".odsc-tile odsc-tile--variant-default odsc-tile--label- product-grid-box"
  );
  const articles = await page.evaluate(() => {
    const articles = document.querySelectorAll(
      ".odsc-tile odsc-tile--variant-default odsc-tile--label- product-grid-box"
    );

    return Array.from(articles).map((article) => {
      try {
        // Go up to the offer-card to find elements
        const offerCard = article.closest(".odsc-tile__inner");

        const title = offerCard?.querySelector(
          ".product-grid-box__title"
        )?.innerText;
        const image = offerCard
          ?.querySelector(".odsc-image-gallery__image")
          ?.getAttribute("src");
        const priceSplashText =
          offerCard?.querySelector(".m-price__label")?.innerText;
        const offerText = offerCard?.querySelector(
          ".m-price__price m-price__price--small"
        )?.innerText;

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

export { LidlScraper };
