# ========== AI_sunda_indo.py ==========
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""Kamu orangnya to the point jadi tidak memakai kata tambahan selain hanya tugas sesuai aturan. jadi hanya tugas menyempurnakan tanpa embel-embel sesuai aturan. Kamu akan menerima teks dalam bahasa Indonesia yang merupakan hasil terjemahan awal dari bahasa Sunda.
             Terjemahan ini masih mentah karena menggunakan pendekatan kata per kata, sehingga bisa terdengar tidak alami atau kehilangan makna aslinya. 
             Tugasmu adalah menyempurnakan terjemahan ini agar menjadi kalimat yang lebih alami dan sesuai dengan konteks aslinya. 
             Berikut beberapa aturan yang harus kamu ikuti: Jangan hanya memperbaiki tata bahasa, tetapi juga pahami makna yang mungkin tersembunyi dalam kata-kata yang kurang tepat. 
             Jika ada kata yang tampak tidak masuk akal (misalnya, 'kata depan' atau 'kata ganti untuk orang pertama' atau kalimat dengan arti panjang), ubah menjadi kata yang lebih sesuai dalam konteks percakapan sehari-hari. jangan hilangkan makna asli dari sebuah kata. 
             Pertahankan nuansa kesopanan dalam bahasa Sunda saat diterjemahkan ke bahasa Indonesia. Jika ada kata yang tampaknya merupakan ekspresi khas dalam bahasa Sunda, ubah menjadi ekspresi yang lebih sesuai dalam bahasa Indonesia. 
             Sekarang, sempurnakan kalimat berikut: {prompt}"""}
        ]
    )
    return response.choices[0].message.content

def ai_translate_fn(original_text, unknown_words):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Kamu adalah penerjemah bahasa Sunda ke bahasa Indonesia. terjemahkan kalimat atau yang ada. Koreksi kata yang typo. Jika ada kata yang tidak kamu kenali, gunakan konteks kalimat untuk mencoba menerjemahkannya. Jika memang tahu segera terjemahkan. Jika tidak yakin, tampilkan kata tersebut dalam italic namun jangan gunakan (*). Jika kata tersebut adalah nama orang, tempat, atau ekspresi umum, jangan terjemahkan."},
            {"role": "user", "content": f"{original_text}\n\nDaftar kata tidak dikenal: {', '.join(unknown_words)}\n\nSilakan terjemahkan kata atau kalimat tersebut sesuai konteks dan ketentuan. jika typo maka koreksi. Jangan keluar konteks dari teks aslinya. dan kasih note 'keterangan: ' jika ada unknown_words."}
        ]
    )

    return response.choices[0].message.content

