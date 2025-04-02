import puppeteer from "puppeteer";

const willysScraper = async () => {
  const url = "https://www.willys.se/erbjudanden/butik";
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

  console.log("starting cookies");
  // Function to reject all cookies
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

  // Call the rejectCookies function
  await rejectCookies(page);
  console.log("ended cookies");
  // Function to click the specified button
  async function clickStoreButton(page) {
    console.log("starting button");
    try {
      // Wait for the button to appear
      const buttonSelector =
        'button[class="sc-59a4afd4-0 fTQtwW sc-9d327e20-2 eheyqd"]';
      await page.waitForSelector(buttonSelector, {
        visible: true,
        timeout: 5000,
      });

      // Force the click using evaluate
      await page.evaluate((selector) => {
        const button = document.querySelector(selector);
        if (button) {
          button.click();
        }
      }, buttonSelector);

      // Wait for the input field to appear
      const inputSelector =
        'input[name="search"][type="search"][placeholder="Sök efter din butik"][class="sc-d4570efb-0 daXCoF sc-75ef2bb4-2 hwqXAv"]';
      await page.waitForSelector(inputSelector, {
        visible: true,
        timeout: 5000,
      });

      // Type "ljungby" into the input field
      await page.type(inputSelector, "ljungby");

      // Wait for a short time
      await page.waitForTimeout(1000);

      // Wait for the list item to appear
      const listItemSelector =
        'div[data-testid="pickup-location-list-item"][data-disabled="false"][class="sc-331fe369-0 iwlvOB"]';
      await page.waitForSelector(listItemSelector, {
        visible: true,
        timeout: 5000,
      });

      // Force the click on the list item using evaluate
      await page.evaluate((selector) => {
        const listItem = document.querySelector(selector);
        if (listItem) {
          listItem.scrollIntoView();
          listItem.click();
        } else {
          console.error("List item not found using evaluate.");
        }
      }, listItemSelector);

      return; // End the function after successful navigation
    } catch (error) {
      console.error("Error clicking the store button:", error);
    } finally {
      console.log("ending button");
    }
  }

  // Call the clickStoreButton function
  await clickStoreButton(page);
  await page.waitForSelector(".sc-7fa12c71-2.bHOIhx");

  // Function to click the "Load More" button until it's no longer visible
  async function autoScroll(page) {
    console.log("autoScroll started");
    try {
      while (true) {
        // Wait for new content to load (adjust time as needed)
        await page.waitForTimeout(2000);

        // Extract articles after loading more content
        const newArticles = await page.evaluate(() => {
          const articles = document.querySelectorAll(".sc-7fa12c71-2.bHOIhx");

          return Array.from(articles).map((article) => {
            try {
              const title = article.querySelector(
                ".sc-7fa12c71-6.gMsSQO"
              )?.innerText;
              const image = article
                .querySelector("img[itemprop='image']")
                ?.getAttribute("src");
              const price = article.querySelector(
                ".sc-49402b38-2.gjPFeg"
              )?.innerText;
              const offerText = article.querySelector(
                ".sc-7fa12c71-14.lbAjba"
              )?.innerText;

              return {
                title: title || null,
                image: image || null,
                price: price || null,
                offerText: offerText || null,
              };
            } catch (error) {
              console.error("Error extracting data:", error);
              return null;
            }
          });
        });

        // Concatenate new articles to allArticles
        allArticles = allArticles.concat(newArticles);

        console.log("start scroll");
        // Simulate scroll wheel
        await page.evaluate(() => {
          window.scrollBy(0, 500); // Adjust the scroll amount as needed
        });
        console.log("end scroll");

        // Wait for the "Load More" button to appear
        const loadMoreButtonSelector = 'button[data-testid="load-more-btn"]';
        try {
          await page.waitForSelector(loadMoreButtonSelector, {
            visible: true,
            timeout: 5000,
          });
          console.log("Load More button found");
        } catch (waitError) {
          console.log("Load More button not found, exiting autoScroll");
          break; // Exit the loop if the button is not found
        }

        // Click the "Load More" button
        try {
          await page.click(loadMoreButtonSelector);
          console.log("Load More button clicked");
        } catch (clickError) {
          console.error("Error clicking Load More button:", clickError);
          break; // Exit the loop if there's an error clicking the button
        }
        // Wait for a short time after scrolling
        await page.waitForTimeout(1000);
      }
    } catch (error) {
      console.error("Autoscroll error:", error);
    }
  }

  // Call the autoScroll function to load all articles
  await autoScroll(page);

  const articles = await page.evaluate(() => {
    const articles = document.querySelectorAll(".sc-7fa12c71-2.bHOIhx");

    return Array.from(articles).map((article) => {
      try {
        const title = article.querySelector(".sc-7fa12c71-6.gMsSQO")?.innerText;
        const image = article
          .querySelector("img[itemprop='image']")
          ?.getAttribute("src");
        const price = article.querySelector(".sc-49402b38-2.gjPFeg")?.innerText;
        const offerText = article.querySelector(
          ".sc-7fa12c71-14.lbAjba"
        )?.innerText;

        return {
          title: title || null,
          image: image || null,
          price: price || null,
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

export { willysScraper };
