from huggingface_hub import login
from transformers import pipeline, BitsAndBytesConfig
import torch
import os
from dotenv import load_dotenv

load_dotenv()
login(token=os.getenv("HUGGINGFACE_TOKEN"))


# def generate_text(prompt, model="gpt-4-turbo"):
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {
#                 "role": "user",
#                 "content": f"Terjemahkan dalam Bahasa Sunda Loma, Tampilkan Hasil terjemahannya saja. Jika menurutmu kata kata yang kamu keluarkan ada bahasa indonesia atau bukan bahasa sunda tolong berikan tanda italic: {prompt}",
#             },
#         ],
#         temperature=0.1,
#     )
#     return response["choices"][0]["message"]["content"]


def generate_text(prompt, pipe):
    print("Model berhasil dimuat dengan 4-bit quantization menggunakan BitsAndBytes!")

    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {"type": "image", "url": "images/ss.png"},
                {
                    "type": "text",
                    "text": f"""abaikan gambar yang saya kirim. Terjemahkan dalam Bahasa Sunda Loma, 
                    Tampilkan Hasil terjemahannya saja. Jika menurutmu kata kata yang kamu keluarkan 
                    ada bahasa indonesia atau bukan bahasa sunda tolong berikan tanda italic: {prompt}
                    """,
                },
            ],
        },
    ]

    output = pipe(text=messages, max_new_tokens=512)
    return output[0]["generated_text"][-1]["content"]
