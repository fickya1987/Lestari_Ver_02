# ai_services.py
from transformers import pipeline
from typing import Optional

class AIService:
    def __init__(self, model_name: str, task: str = "text-generation"):
        self.pipe = pipeline(task, model=model_name)
    
    def generate_text(self, prompt: str, instruction: str) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{instruction}: {prompt}"}
        ]
        output = self.pipe(text=messages, max_new_tokens=512)
        return output[0]["generated_text"][-1]["content"]

# Specific implementations
class Chatbot(AIService):
    def chat(self, prompt: str) -> str:
        instruction = "Anda adalah chatbot Teman percakapan saya. Gunakan Bahasa Sunda Loma untuk menjawab"
        return self.generate_text(prompt, instruction)

class IndoToSundaTranslator(AIService):
    def translate(self, text: str) -> str:
        instruction = """Terjemahkan dalam Bahasa Sunda Loma, Tampilkan Hasil terjemahannya saja. 
        Jika menurutmu kata kata yang kamu keluarkan ada bahasa indonesia atau bukan bahasa sunda 
        tolong berikan tanda italic"""
        return self.generate_text(text, instruction)

class SundaToIndoTranslator(AIService):
    def translate(self, text: str) -> str:
        instruction = """Sempurnakan terjemahan dari bahasa Sunda ke Indonesia ini agar menjadi 
        kalimat yang lebih alami dan sesuai dengan konteks aslinya"""
        return self.generate_text(text, instruction)
