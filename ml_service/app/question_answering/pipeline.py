from openai import OpenAI
import os
import requests

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_general_question(question: str) -> str:
    system_prompt = (
        "You are an intelligent assistant designed to help blind users. "
        "Answer the question clearly, concisely, and in plain language. "
        "Avoid referring to visuals. Speak as if you're reading out loud."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
    )

    return response.choices[0].message.content.strip()
