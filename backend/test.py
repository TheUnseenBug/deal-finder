import subprocess
import asyncio
from pyppeteer import launch
import json
import sys
import re  # Import the regular expression module
from ollama import Client

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
    """
    Runs the DeepSeek model with the given prompt and scraped article data.
    """
    try:
        # Convert the articles data to a JSON string
        articles_json = json.dumps(articles, ensure_ascii=False)
        
        # Create the prompt with the articles data
        full_prompt = f"""
        Task: Convert the following product data into a structured JSON array.
        Each product should have these fields: title, price, category, offerText.
        
        Rules:
        1. Return ONLY valid JSON, no other text
        2. Use appropriate categories like "Dairy", "Meat", "Produce", etc.
        3. Keep all original text values as they are
        4. If a field is missing, use null
        
        Input data:
        {articles_json}
        
        Expected format:
        [
          {{
            "title": "Product Name",
            "price": "Price Value",
            "category": "Category Name",
            "offerText": "Offer Text"
          }},
          ...
        ]
        """
        
        # Create Ollama client
        client = Client(host='http://localhost:11434')
        
        # Generate response using a different model that's better at structured output
        response = client.chat(
            model='mistral:7b',  # Using Mistral which tends to be better at following structured output instructions
            messages=[{
                'role': 'user',
                'content': full_prompt
            }]
        )
        
        # Extract content from response
        if response and 'message' in response:
            content = response['message']['content'].strip()
            
            # Try to find JSON array in the response
            json_match = re.search(r"\[\s*\{.*\}\s*\]", content, re.DOTALL)
            if json_match:
                try:
                    # Clean up the JSON string
                    json_string = json_match.group(0)
                    # Remove any potential markdown code block markers
                    json_string = re.sub(r"```json\s*|\s*```", "", json_string)
                    # Parse the JSON
                    return json.loads(json_string)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    print(f"Problematic JSON: {json_string}")
            else:
                print("No JSON array found in response!")
                print(f"Full response: {content}")
        
        return None

    except Exception as e:
        print(f"Error running DeepSeek: {e}")
        return None


async def main():
    articles = await ica_scraper()
    if articles:
        # Process articles in chunks
        chunk_size = 5  # Adjust this based on the LLM's context window
        categorized_items = []

        for i in range(0, len(articles), chunk_size):
            chunk = articles[i : i + chunk_size]
            response = run_deepseek(None, chunk)  # We don't need the prompt parameter anymore

            if response:
                categorized_items.extend(response)
            else:
                print("Failed to get a response from DeepSeek for a chunk.")

        if categorized_items:
            print("DeepSeek's Categorized Items:")
            print(json.dumps(categorized_items, indent=4, ensure_ascii=False))
        else:
            print("No items were categorized.")
    else:
        print("Failed to scrape articles.")


if __name__ == "__main__":
    asyncio.run(main())
