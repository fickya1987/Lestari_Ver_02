from transformers import pipeline, BitsAndBytesConfig
import torch

from huggingface_hub import login
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
#                 "content": f"""Kamu akan menerima teks dalam bahasa Indonesia yang merupakan hasil terjemahan awal dari bahasa Sunda. Terjemahan ini masih mentah karena menggunakan pendekatan kata per kata, sehingga bisa terdengar tidak alami atau kehilangan makna aslinya. Tugasmu adalah menyempurnakan terjemahan ini agar menjadi kalimat yang lebih alami dan sesuai dengan konteks aslinya.
#                             Berikut beberapa aturan yang harus kamu ikuti:
#                             Jangan hanya memperbaiki tata bahasa, tetapi juga pahami makna yang mungkin tersembunyi dalam kata-kata yang kurang tepat.
#                             Jika ada kata yang tampak tidak masuk akal (misalnya, "kata depan" atau "kata ganti untuk orang pertama"), ubah menjadi kata yang lebih sesuai dalam konteks percakapan sehari-hari.
#                             Pertahankan nuansa kesopanan dalam bahasa Sunda saat diterjemahkan ke bahasa Indonesia.
#                             Jika ada kata yang tampaknya merupakan ekspresi khas dalam bahasa Sunda, ubah menjadi ekspresi yang lebih sesuai dalam bahasa Indonesia.
#                             Jaga agar hasil akhir tetap terdengar seperti percakapan alami dan sopan.
#                             Sekarang, sempurnakan kalimat berikut: {prompt}""",
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
                    "text": f"""abaikan gambar yang saya kirim. Kamu akan menerima teks dalam bahasa Indonesia yang merupakan hasil terjemahan awal dari bahasa Sunda. Terjemahan ini masih mentah karena menggunakan pendekatan kata per kata, sehingga bisa terdengar tidak alami atau kehilangan makna aslinya. Tugasmu adalah menyempurnakan terjemahan ini agar menjadi kalimat yang lebih alami dan sesuai dengan konteks aslinya.
                            Berikut beberapa aturan yang harus kamu ikuti:
                            Jangan hanya memperbaiki tata bahasa, tetapi juga pahami makna yang mungkin tersembunyi dalam kata-kata yang kurang tepat.
                            Jika ada kata yang tampak tidak masuk akal (misalnya, "kata depan" atau "kata ganti untuk orang pertama"), ubah menjadi kata yang lebih sesuai dalam konteks percakapan sehari-hari.
                            Pertahankan nuansa kesopanan dalam bahasa Sunda saat diterjemahkan ke bahasa Indonesia.
                            Jika ada kata yang tampaknya merupakan ekspresi khas dalam bahasa Sunda, ubah menjadi ekspresi yang lebih sesuai dalam bahasa Indonesia.
                            Jaga agar hasil akhir tetap terdengar seperti percakapan alami dan sopan.
                            Sekarang, sempurnakan kalimat berikut: {prompt}""",
                },
            ],
        },
    ]

    output = pipe(text=messages, max_new_tokens=512)
    return output[0]["generated_text"][-1]["content"]
