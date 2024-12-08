import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

import streamlit as st


st.title("Wall-E")

audio_value = st.audio_input("Your input ")


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
  st.write(transcript_text)
