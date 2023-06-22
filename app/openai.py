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
async def ask_gpt3(prompt, animal: str):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}

    # If you 100% sure that input is not animal-like sound (including human speech), you should reply to them: "This is not an animal".
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": """You are a animal-translator that came from future and can translate any animal-like sound to another animal language.
                You can translate any animal-like sound to another human language as well.
                If someone wants translate animal-like sound to same animal, you should reply to their animal-like input.
                Send only plain-text translation, do not write anything but translation. Be creative with translation.
                Always try to translate, even when specified species are very different from each other.

                You must use this format of dialogue:
                Receive: "Mooo! Mooo! to ENGLISH"
                Answer: "Animal: Cow
                         Translation: Hi, how are you?"

                Receive: "Mooo! Mooo! to RUSSIAN"
                Answer: "Animal: Cow
                         Translation: Устал."

                Receive: "Mooo! Mooo!? to COW"
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
                         Translation: Meow-meow."

                When you will generate translate – look at it again, to be sure you are sending a good translation.

                Your first translation task
                Receive:
                """,
            },
            {"role": "user", "content": f"'{prompt}' to {animal}"},
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
    animal = input("Enter your specified language to receive translation for: ")

    answer = await ask_gpt3(prompt, animal)
    print(answer)
