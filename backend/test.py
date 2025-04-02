import requests
from bs4 import BeautifulSoup
import subprocess
import json
import time
import os
import tempfile

def scrape_lidl():
    url = "https://www.lidl.se/c/mandag-soendag/a10066884?channel=store&tabCode=Current_Sales_Week"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        return html_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None


def run_deepseek(prompt, html_file_path):
    """
    Runs the DeepSeek model with the given prompt and a path to an HTML file.

    Args:
        prompt (str): The prompt to send to the DeepSeek model.
        html_file_path (str): The path to the HTML file containing the data.

    Returns:
        str: The response from the DeepSeek model, or None if an error occurred.
    """
    try:
        # Construct the ollama command
        command = [
            'ollama', 'run', 'deepseek-r1:1.5b', f"{prompt}. Use the data from this file:{html_file_path} to generate the table in SEK."
        ]

        # Execute the command and capture the output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        # Decode the output
        response_text = output.decode('utf-8').strip()

        return response_text

    except Exception as e:
        print(f"Error running DeepSeek: {e}")
        return None


if __name__ == '__main__':
    html_content = scrape_lidl()

    if html_content:
        # Create a temporary file to store the HTML content, specifying UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode='w', delete=True, suffix=".html", encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_file.flush()  # Ensure data is written to disk

            # Construct the user prompt, now without the HTML
            user_prompt = "Create a table with the name, size, price, original price, discount, how many for that price return SEK and categorize them."

            # Run DeepSeek with the prompt and the path to the HTML file
            response = run_deepseek(user_prompt, temp_file.name)

            if response:
                print("DeepSeek's Response:")
                print(response)
            else:
                print("Failed to get a response from DeepSeek.")
    else:
        print("Failed to scrape Lidl data.")
