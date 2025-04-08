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
    Kör DeepSeek-modellen med den angivna prompten och de skrapade artikeldata.
    """
    try:
        # Convert the articles data to a JSON string
        articles_json = json.dumps(articles, ensure_ascii=False)
        
        # Create the prompt with the articles data
        full_prompt = f"""
          Uppgift: Konvertera följande produktdata till en strukturerad JSON-array.
    Varje produkt ska ha dessa fält: titel, pris, kategori, erbjudandetext.
    
    Regler:
    1. Returnera ENDAST giltig JSON, ingen annan text
    2. Använd lämpliga kategorier som "Mejeri", "Kött", "Grönsaker", etc.
    3. Behåll alla ursprungliga textvärden som de är
    4. Om ett fält saknas, använd null
    5. INKLUDERA INGA kommentarer i JSON
    6. ANVÄND INTE enkla citat för strängar, använd dubbla citat
    7. INKLUDERA INTE avslutande komman
    8. INKLUDERA INTE bildfältet i ditt svar - vi lägger till det senare
    
    Indata:
        {articles_json}
        
         Förväntat format:
    [
      {{
        "titel": "Produktnamn",
        "pris": "Priskategori",
        "kategori": "Kategorinamn",
        "erbjudandetext": "Erbjudandetext"
      }},
      {{
        "titel": "En annan produkt",
        "pris": "Ett annat pris",
        "kategori": "En annan kategori",
        "erbjudandetext": "Ett annat erbjudande"
      }}
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
                    # Remove any comments
                    json_string = re.sub(r"//.*?$", "", json_string, flags=re.MULTILINE)
                    # Remove any trailing commas
                    json_string = re.sub(r",\s*}", "}", json_string)
                    json_string = re.sub(r",\s*\]", "]", json_string)
                    
                    # Parse the JSON
                    result = json.loads(json_string)
                    
                    # Add back the image URLs from the original articles
                    for i, item in enumerate(result):
                        if i < len(articles) and 'image' in articles[i]:
                            item['image'] = articles[i]['image']
                    
                    return result
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    print(f"Problematic JSON: {json_string}")
                    
                    # Try a more aggressive approach to fix the JSON
                    try:
                        # Extract each item individually using regex
                        items = []
                        item_matches = re.finditer(r'{\s*"title":\s*"([^"]*)",\s*"price":\s*"([^"]*)",\s*"category":\s*"([^"]*)",\s*"offerText":\s*"([^"]*)"', json_string)
                        
                        for i, match in enumerate(item_matches):
                            if i < len(articles):
                                item = {
                                    "title": match.group(1),
                                    "price": match.group(2),
                                    "category": match.group(3),
                                    "offerText": match.group(4),
                                    "image": articles[i].get('image', None)
                                }
                                items.append(item)
                        
                        if items:
                            return items
                    except Exception as e2:
                        print(f"Error extracting items with regex: {e2}")
                        
                        # Last resort: use the original articles data
                        try:
                            # Create a simplified version of the articles with just the essential fields
                            items = []
                            for article in articles:
                                item = {
                                    "title": article.get('title', ''),
                                    "price": article.get('price', ''),
                                    "category": "Unknown",  # We can't determine this without the LLM
                                    "offerText": article.get('offerText', ''),
                                    "image": article.get('image', None)
                                }
                                items.append(item)
                            return items
                        except Exception as e3:
                            print(f"Error creating simplified items: {e3}")
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
