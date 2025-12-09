import os

import requests

from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("HF_API_KEY")


API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"


headers = {"Authorization": f"Bearer {api_key}"}


print("🤖 Welcome to Hugging Face Chatbot! Type 'exit' to quit.")


while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":

        break

    # Correct payload: just a string, not dict inside 'inputs'

    payload = {"inputs": user_input}

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:

        result = response.json()

        # result is a list of dicts with generated_text key

        if isinstance(result, list) and "generated_text" in result[0]:

            reply = result[0]["generated_text"]

        else:

            reply = "Sorry, I didn't get that."

    else:

        reply = f"API Error: {response.status_code}"

    print("Bot:", reply.strip())
