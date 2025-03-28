import streamlit as st
from ai_services import Chatbot
from constraint1 import highlight_text
from constraint2 import process_and_translate
import pandas as pd

def init_chatbot():
    return Chatbot("your-model-name-here")

def chat_interface(df_kamus):
    st.title("Chatbot Lestari")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ketik pesan anda..."):
        chatbot = init_chatbot()
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            response = chatbot.chat(prompt)
            highlighted = highlight_text(response, df_kamus)
            st.markdown(highlighted, unsafe_allow_html=True)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": highlighted})
