import os
import re

import aiohttp
from dotenv import load_dotenv

# Set up your API credentials
load_dotenv()
api_key = os.environ.get("API_KEY")
if not api_key:
    exit(1)

# Define the endpoint URL
url = "https://api.openai.com/v1/chat/completions"


async def ask_gpt3(prompt, animal: str):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": """You are a translator that came from future and can translate from any language to any language, even from animal to animal.
                You can translate any animal-like sound to another human language as well.
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
            answer = re.split(r":|\n", answer)
            answer_list = []
            for a in answer:
                if a.startswith(" "):
                    a = a[1:]
                answer_list.append(a)
            return (answer_list[1], answer_list[3])
