import asyncio
import json
import os

import aiohttp
from dotenv import load_dotenv

# Set up your API credentials
load_dotenv()
api_key = os.environ.get("API_KEY")
if not api_key:
    exit(1)

# Define the endpoint URL
url = "https://api.openai.com/v1/chat/completions"


# Create an asynchronous function to make the API request
async def ask_gpt3(prompt):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": """You are a playing with a child, and imagine that you can translate any animal-like sound to another animal language.
                If someone sends you not animal-like sound, you should reply to them that this is not an animal.
                If someone wants translate animal-like sound to same animal, you should reply to their animal-like input.
                Send only plain-text translation, do not write anything but translation. Be creative with translation.
                Always try to translate, even when specified species are very different from each other.

                You must use this format of dialogue:
                Receive: "Mooo! Mooo! to ENGLISH"
                Answer: "Animal: Cow
                         Translation: Hi, how are you?"

                Receive: "Mooo! Mooo! to COW"
                Answer: "Animal: Cow
                         Translation: Mooo! Mooo!?"

                Receive: "Mooo! Mooo! to FISH"
                Answer: "Animal: Cow
                         Translation: Blob blob blob. Blob."
                Receive: "'Hi, I am John' to ENGLISH"
                Answer: "Animal: Human
                         Translation: Hi, I am John"

                Receive: "'Hi, I am John' to COW"
                Answer: "Animal: Human
                         Translation: Moooooooo!! Mooo."

                Receive: "'Moooo.' to CAT"
                Answer: "Animal: Cow
                         Translation: I want to eat."
                """,
            },
            {"role": "user", "content": prompt},
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            response_data = await response.json()

            # Extract and return the generated answer
            answer = response_data["choices"][0]["message"]["content"]
            return answer


# Example usage
async def main():
    prompt = input("Enter your animal speech that you wish to translate: ")
    answer = await ask_gpt3(prompt)
    print(answer)


# Run the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
