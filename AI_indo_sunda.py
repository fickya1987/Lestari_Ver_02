# ========== AI_indo_sunda.py ==========
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Terjemahkan dalam Bahasa Sunda Loma: {prompt}"}
        ]
    )
    return response.choices[0].message.content
