from huggingface_hub import login
from transformers import pipeline, BitsAndBytesConfig
import torch

# def generate_text(prompt, chat_history, model="gpt-4-turbo"):
#     messages = [{"role": "system", "content": "You are a helpful assistant."}]

#     # Menambahkan riwayat percakapan ke dalam messages
#     for user_msg, bot_msg in chat_history:
#         messages.append({"role": "user", "content": user_msg})
#         messages.append({"role": "assistant", "content": bot_msg})

#     # Menambahkan input terbaru dari pengguna
#     messages.append(
#         {
#             "role": "user",
#             "content": f"Anda adalah chatbot Teman percakapan saya. Gunakan Bahasa Sunda Loma untuk menjawab: {prompt}",
#         }
#     )

#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages,
#         temperature=0.1,
#     )

#     return response["choices"][0]["message"]["content"]


def generate_text(prompt, pipe):
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
                    "text": f"Anda adalah chatbot Teman percakapan saya. Gunakan Bahasa Sunda Loma untuk menjawab: {prompt}",
                },
            ],
        },
    ]

    output = pipe(text=messages, max_new_tokens=512)
    return output[0]["generated_text"][-1]["content"]
