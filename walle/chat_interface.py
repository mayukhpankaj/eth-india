import streamlit as st
from api_utils import get_api_response
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()



import streamlit as st


def display_chat_interface():
    # Chat interface
    audio_value = st.audio_input("voice",label_visibility="hidden")

    context_prompt = """The transcript is about crypto wallet that SEND Cryptocurrency to wallet address or domain name like base.eth  user might say "base dot eth" convert it to "base.eth" example transcript "SEND 1 ETH TO {name}.BASE.ETH" its in the format "SEND {number} TO {domain name}"

FREQUENT WORDS are SEND, SHOW, ETH, ETHEREUM, TO, BALANCE, TRANSFER """

  # Force output in English

    if audio_value:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file = audio_value,
            language="en",
            prompt=context_prompt
        )

        transcript_text = transcript.text
        word_to_symbol = {
            "DOT": ".",
        }

        for word, symbol in word_to_symbol.items():
            transcript_text = transcript_text.replace(word.upper(), symbol)

        st.session_state.messages.append({"role": "user", "content": transcript_text})
 

        with st.spinner("Generating response..."):
            response = get_api_response(transcript_text, st.session_state.session_id, st.session_state.model)
            
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response['answer']})               
                       
            else:
                st.error("Failed to get a response from the API. Please try again.")


    st.session_state.model = "gpt-4o"
    st.session_state.session_id = "123"

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Query:" ) :
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)
            
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response['answer']})
                
                with st.chat_message("assistant"):
                    st.markdown(response['answer'])
                    
                       
            else:
                st.error("Failed to get a response from the API. Please try again.")