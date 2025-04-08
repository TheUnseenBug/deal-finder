import requests
from bs4 import BeautifulSoup
import subprocess
import tempfile
import asyncio
from pyppeteer import launch
import json
import sys
print(sys.executable)


async def ica_scraper():
    url = "https://www.ica.se/erbjudanden/maxi-ica-stormarknad-ljungby-1004102/"
    try:
        browser = await launch(
            executablePath=(
                "C:\\Users\\denni\\.cache\\puppeteer\\chrome\\win64-121.0.6167.85"
                "\\chrome-win64\\chrome.exe"
            ),
            headless=False,
        )
        page = await browser.newPage()
        await page.goto(url, {"waitUntil": "networkidle2"})
        await page.waitForSelector(".offer-card__info-container")

        articles = await page.evaluate(
            """() => {
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
          }"""
        )

        await browser.close()
        return articles

    except Exception as e:
        print(f"Error during scraping: {e}")
        return None


def run_deepseek(prompt, articles):
    try:
        # Convert the articles data to a JSON string
        articles_json = json.dumps(articles, ensure_ascii=False)

        command = [
            "ollama",
            "run",
            "deepseek-r1:8b",
            f"""{prompt} 
            {articles_json}
            Make sure to extract the information accurately.
            If a value is not present, leave it blank.""",
        ]

        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = process.communicate()

        response_text = output.decode("utf-8").strip()

        return response_text

    except Exception as e:
        print(f"Error running DeepSeek: {e}")
        return None


async def main():
    articles = await ica_scraper()
    if articles:
        user_prompt = """ I want you to categorize every item in the articles array and make it into json data
        """
        response = run_deepseek(user_prompt, articles)

        if response:
            print("DeepSeek's Response:")
            print(response)
        else:
            print("Failed to get a response from DeepSeek.")
    else:
        print("Failed to scrape articles.")


if __name__ == "__main__":
    asyncio.run(main())